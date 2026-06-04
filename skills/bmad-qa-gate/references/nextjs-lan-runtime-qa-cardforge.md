# Next.js LAN Runtime QA Pattern — CardForge CF-E1-S7 (2026-05-26)

## When this applies

Use when a BMad web app has passed code review but still needs founder/manual runtime smoke before Vercel or public deployment.

## Pattern

1. Inspect current BMad state and repo cleanliness first:
   - `_bmad/state.json` should distinguish `code-reviewed, runtime-unverified` from QA/founder readiness.
   - Check git status/HEAD so local runtime does not start from stale or uncommitted surprise state.
2. Verify runtime prerequisites without printing secrets:
   - `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, and `DATABASE_URL` presence.
   - Node/package-manager version.
   - LAN IP with `hostname -I`.
   - Port availability with `ss -ltnp 'sport = :3000'` or equivalent.
3. Prefer local/LAN runtime before Vercel for first founder smoke:
   - Build first: `corepack pnpm build`.
   - Start production server on all interfaces: `./node_modules/.bin/next start -H 0.0.0.0 -p 3000`.
   - For long-lived background hosting under Hermes, if normal background process supervision drops the server silently, use a tiny detached launcher script under an ignored local runtime directory (for example `.run/start_cardforge.py`) that records PID/logs. Do not commit `.run/`; add it to `.gitignore` if needed.
4. Verify from both loopback and LAN address:
   - `curl -I http://127.0.0.1:3000/login`
   - `curl -I http://<LAN_IP>:3000/login`
   - Record HTTP status and the access URL for the user.
5. Give the user a concise smoke checklist:
   - login/sign-up, dashboard redirect, sign-out, lot/card creation, sale, expense, dashboard update, CSV export.
6. If Supabase Auth redirects fail on LAN, add the LAN origin and dashboard URL to Supabase allowed/site redirect URLs:
   - `http://<LAN_IP>:3000`
   - `http://<LAN_IP>:3000/dashboard`

## Evidence boundary

A local server being reachable is not itself QA pass. It is runtime availability for manual QA. Keep gate verdict as `code-reviewed, runtime-unverified` until the user or agent actually completes and records the smoke path.

## Pitfalls

- `next dev -H 127.0.0.1` is not LAN-accessible; bind to `0.0.0.0` for same-LAN browser testing.
- `corepack pnpm exec next start ...` may be fine foreground but can be awkward under Hermes background supervision; direct `./node_modules/.bin/next start` is simpler.
- Do not deploy to Vercel just to test the first local runtime path when the user prefers to wait until feature-complete.
- Do not commit PID/log/runtime launcher artifacts; keep them under ignored `.run/` or equivalent.
