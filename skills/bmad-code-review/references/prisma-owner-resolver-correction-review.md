# Prisma / Next Owner Resolver Correction Review Pattern

Use this when reviewing BMad stories that add owner-scoped Prisma repositories, server actions, or App Router pages before full auth UX is complete.

## Durable lesson

A correction that only replaces `const ownerId = 1` with an environment-only helper such as `getDevOwnerId()` may remove the literal hardcode but can still leave production routes/actions mapped through a development seam. For production-facing pages/actions, prefer a centralized resolver with this shape:

1. Server-only module.
2. Preferred path: current Supabase/session user -> `UserProfile.auth_uid` lookup -> owner id.
3. Explicit local-dev fallback: `OWNER_ID` is allowed only as an opt-in development seam.
4. Production guard: fallback is disabled in production unless a deliberately named override such as `ALLOW_DEV_OWNER_ID=true` is present.
5. Failure mode: throw explicit owner-unavailable errors rather than silently returning owner `1`.

## Review checklist

- Search pages, route handlers, and server actions for `ownerId = 1`, `getDevOwnerId`, `OWNER_ID`, or equivalent owner resolver shortcuts.
- If full auth UX is out of story scope, verify the resolver is still safe: auth/session-first, centralized, explicit fallback, production-gated, and no silent default.
- Confirm build-time dynamic rendering does not hide the problem. A dynamic route that still maps every request to the same owner remains a blocker.
- Update BMad artifacts to distinguish:
  - code-review progression (`PASS WITH NOTES` may be acceptable), from
  - full auth UX, live Supabase/RLS verification, and runtime/founder QA (separate gates).
- Re-run the validation bundle after any resolver changes because importing Supabase server helpers into pages/actions can affect Next build behavior.

## Verdict guidance

- `BLOCKED`: production-facing pages/actions still use literal owner `1` or an ungated dev-only resolver that can silently serve/write one shared owner in normal production paths.
- `PASS WITH NOTES`: the resolver is auth/session-first and production-gated, but full auth UX or live Supabase/RLS smoke remains deferred by story scope.
