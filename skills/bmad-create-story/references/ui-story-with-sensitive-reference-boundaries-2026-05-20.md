# UI Story Creation with Sensitive Reference Boundaries — 2026-05-20

Use this pattern when creating a BMad story for an operator-facing UI surface that touches checkout identity, worker controls, or other sensitive domains while runtime implementation is not yet complete.

## Trigger

A story is selected from canonical planning and needs to become `ready_for_dev`, but the UI scope includes fields such as account/session, shipping, payment, route policy, auto-submit policy, live browser controls, logs, or cart state.

## Pattern

1. Ground the story in canonical planning first:
   - `epics_and_stories.md` for story text, scope, ACs, dependencies, traceability.
   - PRD/UX/architecture sections for required fields, UI affordances, and runtime boundaries.
   - Prior story artifacts for carry-forward constraints.

2. Inspect current code reality before writing the story:
   - Identify the actual route/screen currently used by the app.
   - If a static renderer route is the real Electron surface, call that out explicitly.
   - Warn against implementing an unused TSX-only surface if the runtime shell still uses another path.

3. Convert sensitive domain fields into opaque/redacted references:
   - account/session reference
   - shipping reference
   - payment reference
   - webhook/secret reference
   - route/proxy reference if credentials may be involved
   - Never put raw credentials, card details, tokens, cookies, OTP values, webhook URLs, or connection strings in story examples, fixtures, tests, logs, or BMad evidence.

4. Preserve runtime evidence boundaries:
   - UI stories can expose controls or command-intent placeholders without claiming live runtime execution.
   - Do not claim browser/profile launch success, Redis events, DB persistence, checkout execution, visual QA, or founder readiness unless separate evidence exists.
   - If a UI action is not runtime-wired, require clear unavailable/placeholder copy rather than pretending success.

5. Make carry-forward constraints actionable in acceptance criteria and dev notes:
   - Profile uniqueness / duplicate config behavior.
   - Auto-submit must be visibly tied to guardrails.
   - Lifecycle/status display must reuse canonical state vocabulary from prior stories.
   - Package-root export/import decisions should be settled before new UI consumers rely on internal module paths.

6. Synchronize artifacts:
   - New story artifact status: `ready_for_dev`.
   - `_bmad/state.json`: `workflow_status: story_created`, `active_workflow: bmad-dev-story`, `next_recommended_workflows: ["bmad-dev-story for <story>"]`.
   - `_bmad/sprint-status.yaml`: append focused story entry without broad YAML reformat.
   - `CONTINUE-HERE.md`: update the top status and any early “active story / next workflow” block; stale first-story recommendations should not remain prominent.

## Example from HLX-5.3

HLX-5.3 created a Checkout Workers UI story that included:
- list/detail UI for workers;
- unique profile assignment enforcement;
- duplicate-worker disabled until a new profile is selected;
- lifecycle status/current task visibility using HLX-5.2 states;
- cart/log panels allowed as redacted placeholders;
- auto-submit copy tied to price/quantity/min-cart/max-spend/final pre-submit guardrails;
- explicit exclusions for checkout execution, Redis events, DB persistence, browser launch claims, and founder readiness.
