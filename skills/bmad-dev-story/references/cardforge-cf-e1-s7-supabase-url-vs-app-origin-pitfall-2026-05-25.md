# CF-E1-S7: Supabase URL vs App-Origin Pitfall

Context:
- Project: CardForge (src/app/(dashboard)/layout.tsx)
- Story: CF-E1-S7 — Auth, Supabase Runtime, and MVP Finish Gate
- Issue: ensure-profile and sign-out wired to NEXT_PUBLIC_SUPABASE_URL instead of app-local routes.

Problem:
- NEXT_PUBLIC_SUPABASE_URL is the Supabase project host (e.g., https://<project>.supabase.co).
- Using it as a base for app API routes (e.g., /api/auth/ensure-profile) sends requests to Supabase, not to the Next.js app.
- Consequences:
  - UserProfile upsert route is never reached.
  - Sign-out route is never reached.
  - Auth cookies are not forwarded as expected.

Correct patterns (for any Next.js + Supabase app):

1. Server-side app-to-app calls (e.g., layout ensuring profile):
   - Derive origin from request headers:
     - const headerStore = await headers();
     - const proto = headerStore.get("x-forwarded-proto") ?? "http";
     - const host = headerStore.get("x-forwarded-host") ?? headerStore.get("host");
     - const base = `${proto}://${host}`;
     - const res = await fetch(`${base}/api/auth/ensure-profile`, { cache: "no-store" });
   - Never: NEXT_PUBLIC_SUPABASE_URL + "/api/auth/ensure-profile".

2. Sign-out:
   - Preferred:
     - Dedicated server action:
       - CreateServerSupabaseClient()
       - await signOut()
       - redirect("/login")
     - Or: form posts to local /api/auth/signout (relative path).
   - Never:
     - fetch to NEXT_PUBLIC_SUPABASE_URL + "/api/auth/signout".

3. Client-side app-to-app calls:
   - Use relative URLs:
     - fetch("/api/auth/ensure-profile")
   - NEXT_PUBLIC_SUPABASE_URL is only for:
     - Initializing Supabase client (createBrowserClient/createServerClient).

Testing:
- Add tests that:
  - Read the layout or relevant files as text.
  - Assert:
    - No app API route (e.g., /api/auth/ensure-profile, /api/auth/signout) is concatenated with NEXT_PUBLIC_SUPABASE_URL.
    - Sign-out does not fetch an external Supabase-project URL.
  - This prevents regressions where wiring is “obviously correct” in local dev (where NEXT_PUBLIC_SUPABASE_URL may be localhost) but broken in production.
