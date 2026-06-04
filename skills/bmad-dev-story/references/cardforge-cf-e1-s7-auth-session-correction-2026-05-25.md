# CF-E1-S7 — Auth/Session Correction Notes (2026-05-25)

## Context

CF-E1-S7 (Auth, Supabase Runtime, and MVP Finish Gate) was BLOCKED twice because:

- The dashboard tried to bootstrap UserProfile via a self-fetch (fetch to /api/auth/ensure-profile) that:
  - Did not forward auth cookies.
  - Silently ignored non-OK responses.
- Sign-out called Supabase signOut() but the server client had no cookie setters, so auth cookies were not cleared.
- Auth tests were file-existence/regex checks that did not fail when these boundaries broke.

## Corrections applied

1) UserProfile bootstrap: direct server helper, no HTTP

- New file: src/lib/auth/ensure-profile.ts
  - export async function ensureCurrentUserProfile(authUid: string): Promise<number>
  - Uses prisma.userProfile.upsert({ where: { auth_uid }, create: { auth_uid }, update: {} })
  - Returns profile.id (owner_id).
- src/app/(dashboard)/layout.tsx:
  - After getUser():
    - await ensureCurrentUserProfile(data.user.id)
  - On failure: redirect("/login") instead of continuing.
  - Removed fetch-based ensureUserProfile().

Key rule:
- For auth-critical, same-process operations (e.g., UserProfile bootstrap in layout), prefer direct server calls over HTTP self-fetches.
- Self-fetch from a server component:
  - May not carry the same cookies.
  - May silently fail.
  - Adds a race and fragility that is unnecessary.

2) Supabase SSR cookie handling for sign-out

- src/lib/auth/server.ts:
  - createServerSupabaseClient now configures:
    - get(name)
    - setAll(allCookies) that writes each cookie via cookieStore.set.
- This is required by @supabase/ssr for auth-changing calls:
  - Without setAll/set/remove:
    - signOut() can “succeed” in the Supabase client but fail to clear cookies.
    - User appears logged out in logic but still has session cookies → confusing behavior.

3) Auth tests: boundary checks over file-existence

- tests/unit/auth-middleware-basic.test.ts extended to assert:
  - Layout imports ensureCurrentUserProfile from @/lib/auth.
  - Layout does not call fetch to /api/auth/ensure-profile.
  - ensure-profile.ts exists and uses prisma.userProfile.upsert (no fetch).
  - server.ts configures setAll/set/remove cookie methods.
  - signout-action and signout route:
    - Use createServerSupabaseClient.
    - Call signOut().
    - Redirect to /login.
  - middleware protects /dashboard and redirects to /login.

**Middleware cookie pattern (CF-E2-S3, 2026-05-28)**:
- Supabase SSR 0.6.1 marks `get`/`set`/`remove` as deprecated.
- Middleware must use `getAll()` and `setAll(cookiesToSet[])`:
  - `getAll()` reads all cookies from the mutable request.
  - `setAll()` writes cookies to the response object.
- Response must use `NextResponse.next({ request: req })` (not `NextResponse.next()`) so the response object is mutable and cookies can be set while reading from the mutable request (`req.cookies.set()` writes to the request and can be read back by the Supabase client).
- Without this, sign-out can appear to succeed but auth cookies are not cleared → user appears logged out but session persists.

Rule:
- For finish-gate auth stories, tests must:
  - Validate the actual auth boundaries (e.g., no Supabase-host regressions, cookie configuration, profile bootstrap method).
  - Not just confirm that files exist or that certain strings appear.
