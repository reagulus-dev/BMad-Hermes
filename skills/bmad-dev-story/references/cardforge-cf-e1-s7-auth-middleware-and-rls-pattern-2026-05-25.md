# CF-E1-S7: Auth, Middleware, Migrations, and RLS Pattern

Source session: CF-E1-S7 on CardForge (2026-05-25).

- Used:
  - @supabase/ssr:
    - createBrowserClient in src/lib/auth/client.ts for login page.
    - createServerClient in src/lib/auth/server.ts for server actions, middleware, and routes.
  - Middleware at src/middleware.ts:
    - Redirect unauthenticated /dashboard to /login.
    - Redirect authenticated /login to /dashboard.
    - Excluded static assets and /api/ from matcher.
  - Dashboard layout:
    - Verifies user via server Supabase client.
    - Calls /api/auth/ensure-profile to upsert UserProfile by auth_uid.
    - Provides sign-out button via form to /api/auth/signout.
  - ensure-profile route:
    - GET /api/auth/ensure-profile:
      - Reads current user from Supabase.
      - Upserts UserProfile row.
      - Returns owner_id.

- Migrations:
  - Ran: prisma migrate status → pending migrations.
  - Ran: prisma migrate deploy → applied to Supabase pooler.
  - For future stories: prefer migrate deploy in remote/production; migrate dev only in local/dev.

- RLS:
  - Queried pg_tables for rowsecurity.
  - All business tables had rowsecurity=false.
  - Recorded as MVP risk: security relies on application-level owner_id enforcement.
  - For multi-user/public deployment: a follow-up story must enable RLS and verify policies.

- Testing notes:
  - Directly importing middleware in unit tests fails due to Next.js runtime specialization.
  - Use file-presence tests or integration-style checks instead.
