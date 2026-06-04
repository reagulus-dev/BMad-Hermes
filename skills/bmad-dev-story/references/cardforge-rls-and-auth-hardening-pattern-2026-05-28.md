# RLS and Auth Hardening Pattern (CardForge CF-E2-S3)

Used: 2026-05-28 for CF-E2-S3 (RLS and Security Hardening).

- RLS:
  - Implemented via Prisma migration using:
    - ALTER TABLE <table> ENABLE ROW LEVEL SECURITY.
    - CREATE POLICY per table (SELECT/INSERT/UPDATE/DELETE) using:
      - auth.uid() → user_profiles.auth_uid → owner_id.
  - Ensures: only authenticated owner can access their rows; no table globally readable/writable.
  - ⚠️ **CRITICAL PITFALL (uuid vs text)**: `auth.uid()` returns `uuid`; `user_profiles.auth_uid` is `text` (Prisma `String`). Direct comparison fails with `operator does not exist: text = uuid`. Every `auth.uid()` reference in RLS policies **must** cast: `auth.uid()::text`
  - Fix at scale with sed:
    ```bash
    sed -i 's/up\.auth_uid = auth\.uid()/up.auth_uid = auth.uid()::text/g' migration.sql
    sed -i 's/auth_uid = auth\.uid()/auth_uid = auth.uid()::text/g' migration.sql
    sed -i 's/auth\.uid()::text::text/auth.uid()::text/g' migration.sql  # clean doubles
    ```
- Auth guard:
  - Introduced requireAuthedOwnerId() that:
    - Calls resolveCurrentOwnerId().
    - Throws a clear AuthError if auth fails or owner ID is invalid.
  - Wired into server actions (inventory, sales, expenses).
- Middleware:
  - Confirmed to protect all /dashboard routes.
  - Redirects:
    - Unauthenticated → /login.
    - Authenticated on /login → /dashboard.
- Testing:
  - RLS behavior validated logically via unit tests (owner-scoped vs cross-owner).
  - E2E smoke test: login + inventory read/write + sales read under RLS.
