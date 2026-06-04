# CF-E1-S7 — Auth/Session Review Correction Notes (2026-05-25)

## Context

CF-E1-S7 (Auth, Supabase Runtime, and MVP Finish Gate) was BLOCKED because:

- The layout used a self-fetch to /api/auth/ensure-profile:
  - Did not forward auth cookies.
  - Silently ignored non-OK responses.
  - Downstream owner-scoped queries would fail with “no UserProfile” if this failed.
- Sign-out used Supabase signOut() but the SSR server client lacked cookie setters, so auth cookies were not cleared.
- Auth tests were file-existence/regex checks that did not fail when these boundaries broke.

## Review-required checks (CF-E1-S7 pattern)

When reviewing a Supabase/Next.js auth finish-gate story, require:

- UserProfile bootstrap:
  - Prefer a server-only helper that:
    - Uses Prisma upsert directly.
    - Is called from the protected layout after getUser().
    - Fails hard (redirect/block) if it cannot create/resolve the profile.
  - If a self-fetch is used:
    - Must forward the current request cookies.
    - Must treat non-OK as fatal for the current page.
    - If not, treat as BLOCKED.

- Sign-out:
  - Must call Supabase signOut() through a server client configured with cookie setters:
    - Prefer `setAll` (modern).
    - Accept deprecated `set`/`remove` if correctly implemented.
  - Without cookie setters, sign-out can redirect while leaving session cookies intact → BLOCKED.

- Tests:
  - Must not rely solely on file-existence or source-presence checks.
  - Must include tests that:
    - Assert layout uses the correct auth boundary (e.g., ensureCurrentUserProfile).
    - Assert layout does not fetch /api/auth/ensure-profile or /api/auth/signout from NEXT_PUBLIC_SUPABASE_URL.
    - Assert the Supabase SSR client configures cookie setters.
    - Prefer at least one test that exercises the cookie adapter (e.g., calling setAll with an array) so wrapper-shaped mistakes fail.

## Outcome

- Correction replaced self-fetch with a direct server helper.
- Supabase SSR setAll was wired.
- Auth tests were strengthened.
- All static gates passed.
- Fresh bmad-code-review required to confirm.

## Additional review pitfall discovered

- If a story AC requires `.env.example` or other runtime documentation to be committed, verify that the file is actually tracked/trackable. A broad `.gitignore` rule such as `.env*` can silently ignore `.env.example`; fix by adding an explicit unignore (`!.env.example`) and stage the example file.
- When writing durable BMad artifacts, do not store credential-shaped placeholders such as `postgresql://placeholder:***@...`; record validation as `DATABASE_URL=[REDACTED] ...` and keep examples in `.env.example` as obvious placeholder tokens.
