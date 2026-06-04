# Finalization story after feature-scope completion

Use this pattern when the planned feature stories for an MVP/epic have passed code review, but the app is not yet human-usable because runtime/auth/deployment setup remains unverified.

## Trigger

- The canonical feature list is complete at code-review gate.
- BMad state/sprint show no product-code blockers for the feature stories.
- Carry-forward notes repeatedly mention runtime/browser smoke, live DB/RLS, auth, deployment, or founder QA.
- The user asks what remains to finish the web app/app/product.

## Pattern

1. Run state-check from project truth: state.json, sprint-status, latest story artifact, planning artifacts, and git status/HEAD.
2. Identify whether the remaining gap is a real human/runtime blocker rather than another planned feature.
3. Create a bounded bridge/finalization story instead of silently advancing to QA or inventing a new feature story.
4. Name it at the epic level, e.g. `<EPIC>-S<N> — Auth, Runtime, and MVP Finish Gate`.
5. Scope the story to the finish gate only:
   - real auth/login/sign-out if still placeholder
   - runtime env verification without leaking secrets
   - live database migration/RLS verification
   - route protection/owner resolution
   - browser smoke over the core user journey
   - clear separation of code-review pass vs QA/founder/release readiness
6. Record exact external blockers in state and continuation docs, e.g. missing pooler `DATABASE_URL`, Supabase Auth settings, redirect URLs, or email-confirmation/rate-limit issues.

## Evidence expectations

- Secret-safe env key presence, not values.
- Project ref/host only when non-secret.
- Migration/RLS evidence separated from browser/Auth UI smoke evidence.
- Static validation bundle plus runtime smoke results.
- If blocked by human setup, stop with the exact setting/key needed rather than pretending the story is complete.
