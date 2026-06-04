# Next.js Supabase Auth Route-Origin Review Pitfall

Use when reviewing Next.js App Router stories that add Supabase Auth login, protected dashboard layouts, profile bootstrap routes, or sign-out routes.

## Durable lesson

`NEXT_PUBLIC_SUPABASE_URL` is the Supabase project origin, not the Next.js application origin. Do not accept production-facing code that builds local app API URLs by appending `/api/...` to `NEXT_PUBLIC_SUPABASE_URL`.

Common broken pattern:

```ts
await fetch(`${process.env.NEXT_PUBLIC_SUPABASE_URL}/api/auth/ensure-profile`)
await fetch(`${process.env.NEXT_PUBLIC_SUPABASE_URL}/api/auth/signout`, { method: "POST" })
```

In production this targets `https://<project>.supabase.co/api/...`, not the app's own route handlers. It also fails to carry the app request/session cookies as intended.

## Review checks

- Inspect protected layouts, server actions, route handlers, and client auth components for app-local API calls.
- Distinguish origins:
  - Supabase origin: `NEXT_PUBLIC_SUPABASE_URL` for Supabase client creation only.
  - App origin: relative route (`/api/auth/signout`), framework server action, `headers()`-derived origin when truly needed, or an explicit app URL env var such as `NEXT_PUBLIC_APP_URL` / `APP_URL`.
- Prefer avoiding self-fetch from server components/layouts when possible:
  - call the underlying server-only function directly, or
  - implement the profile bootstrap/sign-out logic in a server action/route that naturally receives the current request cookies.
- Verify sign-out UX path hits the app-local route/server action and redirects/navigates correctly.
- Verify first-authenticated-user profile bootstrap actually creates/resolves the owner/profile row through the app boundary before owner-scoped pages call the owner resolver.

## Evidence expectations

File-existence tests are not meaningful evidence for this class of story. Source-regex tests are useful as regression guards for a specific URL-origin bug, but they are not sufficient evidence for cookie/session-sensitive auth behavior. Require focused regression tests or runtime smoke that would fail if:

- app API calls are pointed at the Supabase project host;
- a server component/layout self-fetches an app-local auth/profile route without forwarding the authenticated request cookies;
- profile bootstrap receives a 401/non-OK response and silently continues instead of failing/redirecting before owner-scoped pages/actions run;
- sign-out redirects but does not clear Supabase auth cookies because the server client boundary lacks cookie setters;
- sign-out does not hit the app-local sign-out boundary;
- profile bootstrap does not receive/use the authenticated app session;
- auth middleware only exists but protected-route behavior is not exercised.

Static validation can pass while these flows are broken. Use `BLOCKED` when the story acceptance criteria require real sign-in/profile/sign-out behavior and the route-origin, cookie-forwarding, cookie-clearing, or boundary-test evidence is wrong or missing.

## Example correction shapes

- For sign-out UI: use a form action that posts to `/api/auth/signout`, or a server action that calls Supabase `auth.signOut()` and `redirect("/login")` directly through a server-client boundary that can actually set/remove cookies (`setAll` preferred, deprecated `set`/`remove` acceptable when already used correctly by the project). A redirect alone is not evidence that the session cookie was cleared.
- For ensure-profile: extract a server-only `ensureCurrentUserProfile()` helper used directly from the protected layout/route after `getUser()`, or call an app-local route with a correct app origin and forwarded `Cookie` header if self-fetch is unavoidable. Do not swallow non-OK profile-bootstrap responses when downstream pages/actions require the profile to exist.
