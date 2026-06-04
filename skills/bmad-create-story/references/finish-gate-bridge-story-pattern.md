# Finish-gate bridge story after code-review-complete MVP slice

Use this pattern when a project’s planned feature stories are complete at code-review gate, but the app is not actually human-usable because runtime setup remains missing.

## Trigger signals

- User asks what is next to “finish the web app/app/product”.
- Sprint/status shows all planned feature stories complete at code-review gate.
- Carry-forward notes repeatedly say runtime/browser QA, live DB/RLS verification, auth setup, deployment env, or founder QA remain deferred.
- Code is statically validated but login/runtime paths are placeholders or require external credentials/settings.

## Pattern

1. Run state-check from repo truth: state, sprint status, planning artifacts, recent commits, and obvious runtime placeholders.
2. Do not call the app finished just because code review passed.
3. Create a bounded bridge/finalization story under the current epic, e.g.:
   - `<EPIC>-S<N> — Auth, Supabase Runtime, and MVP Finish Gate`
4. Scope the story to concrete finish blockers only:
   - auth/sign-in/sign-out
   - authenticated owner/profile resolution
   - protected routes
   - live DB migration/status verification
   - RLS policy posture/behavior verification or explicit accepted risk note
   - browser/runtime smoke through the core user journey
   - deployment/env verification if relevant
5. Capture external/human blockers explicitly in the story and state:
   - missing pooler `DATABASE_URL`
   - Supabase Auth provider/email-confirmation/redirect URL settings
   - missing deployment env vars
   - unreachable direct DB host from the agent environment
6. Set next workflow to `bmad-dev-story for <finish-gate-story>`, but do not proceed to dev-story if the user only asked to verify env/status.

## Evidence hygiene

- Verify `.env` secret-safely: presence, host/ref, JWT safe claims, endpoint status; never print values.
- Distinguish database verification from auth UI smoke and from release/founder readiness.
- Commit story/status artifacts separately from implementation when possible.
