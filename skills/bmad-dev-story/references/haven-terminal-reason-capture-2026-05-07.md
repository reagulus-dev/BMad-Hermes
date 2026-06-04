# Haven terminal booking reason capture — 2026-05-07

Reusable pattern for cancellation/no-show reason capture in booking/reservation operational flows.

## Class pattern
When a booking leaves active operational worklists through a terminal status (`cancelled`, `no_show`), capture a structured reason at the transition boundary, not as loose notes and not after the fact.

## Implementation pattern
- Add structured fields on the booking/reservation row, e.g. `cancellation_reason`, `no_show_reason`, and `status_reason_recorded_at`.
- Extend the shared status-transition RPC/service rather than adding separate direct update paths.
- Require a non-empty reason for `cancel` and `no_show`; reject blank/whitespace input at both service/UI and RPC layers.
- Preserve other transitions: `check_in` / `check_out` should not require or store terminal-reason fields unless the product explicitly says so.
- In the operator UI, make terminal actions open a reason panel/modal before executing the transition.
- After transition, refresh Today/operations read models and prove terminal rows leave active worklists.
- Display structured reasons in Bookings/history so terminal rows remain explainable.

## DB hardening pattern
- Use a trusted transactional transition RPC for status + reason updates.
- Add guards so direct app-flow `UPDATE` attempts to terminal reason fields are rejected outside the trusted transition path.
- Also guard direct `INSERT` attempts with prefilled terminal-reason fields; review caught that UPDATE-only guards left an insert bypass.
- Smoke-test both direct update and direct insert rejection.

## Validation pattern
- Service/RPC smoke should prove:
  - cancel without reason rejected,
  - no-show without reason rejected,
  - cancel stores only `cancellation_reason`,
  - no-show stores only `no_show_reason`,
  - checkout/check-in do not store terminal reasons,
  - direct terminal-reason update rejected,
  - direct terminal-reason insert rejected.
- Browser/runtime QA should prove:
  - cancel/no-show reason panel appears,
  - row leaves Today after reason submit,
  - structured reasons appear in Bookings/history,
  - console errors are zero.
- Android build/install/launch smoke is useful packaging evidence but is not full native terminal-reason interaction automation.

## Pitfalls
- Do not treat freeform notes as sufficient terminal-reason capture when the business needs explainable cancellation/no-show history.
- Do not execute Cancel/No-show immediately from Today if the story requires reasons; the reason capture must block transition execution.
- Do not only guard direct updates; direct inserts with prefilled terminal reason fields can bypass reason provenance unless explicitly rejected.
- Do not remove terminal bookings from all user-visible history; remove from active Today worklists but keep status/reason visible in Bookings/history.
- Do not claim Android interaction verification from APK build/install/launch alone.

## Evidence anchor from session
- Story: `_bmad/artifacts/stories/4-9-cancellation-no-show-reason-capture.md`
- Consolidated evidence: `_bmad/artifacts/evidence/terminal-reason-capture-20260507133714/summary.json`
- Browser QA evidence: `_bmad/artifacts/evidence/browser-terminal-reasons-20260507133411/summary.json`
- Final review verdict: PASS after direct-insert guard was added.
