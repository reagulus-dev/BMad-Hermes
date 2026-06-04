# Founder Smoke Triage Pattern

Use this reference when a founder/user manually smoke-tests a BMad-managed app after a story has passed code review with notes, then reports runtime behavior.

## Core principle

Do not collapse all founder smoke feedback into either “already planned later” or “fix immediately.” First classify each observation against the project truth:

1. Canonical PRD/product semantics.
2. Current epic/story acceptance criteria.
3. Story review notes and explicit deferred gates.
4. Source/runtime reality if tools are available.
5. Whether the observation blocks the current gate.

## Procedure

1. Read `_bmad/state.json`, `_bmad/sprint-status.yaml`, the active story artifact, `CONTINUE-HERE.md`, and relevant planning artifacts.
2. Identify whether the project is at:
   - code-review complete only,
   - runtime/browser smoke pending,
   - founder QA pending,
   - release/security gate pending.
3. For each user-reported issue, label it as one of:
   - **expected product semantics** — behavior matches PRD/architecture;
   - **unverified runtime gap** — within a deferred smoke/QA gate;
   - **real defect/regression** — contradicts acceptance criteria or implementation intent;
   - **UX/polish gap** — usable but hostile, especially when the PRD says a user-facing concept should be friendlier than the persistence model;
   - **out-of-scope future epic** — clearly covered by a deferred epic or not needed for the current gate.
4. If the app is reported as hanging/unreachable and tools are available, do read-only probes first:
   - process and port listener;
   - HTTP timing/headers/body probe;
   - server logs if available;
   - resource/socket state if the process is alive but unresponsive.
   Do not restart or mutate runtime state unless the user asks or the active workflow authorizes repair.
5. Map accounting/data-model confusion carefully:
   - Lot/inventory acquisition cost often belongs to COGS.
   - Expenses are usually separate business expenses.
   - A lot cost not appearing in Expenses may be correct even if it should appear in dashboard COGS/profit.
6. Map money-input UX separately from persistence:
   - Integer pence persistence can be correct.
   - User-facing forms should still accept GBP decimal values when the PRD says currency is GBP or another similar user-friendly currency model.
7. Recommend the next valid BMad workflow/gate, such as:
   - `bmad-dev-story correction for <story> runtime/founder smoke`,
   - `bmad-code-review` after correction,
   - dedicated QA/runtime verification gate,
   - or a future story only when the artifact-backed scope supports it.

## Reporting format

Keep the report operational:

- Current state / trust level.
- Runtime health if checked.
- Issue-by-issue classification.
- What is normal vs not normal.
- Next valid workflow.

Avoid implying that `PASS WITH NOTES` means founder-usable, browser-smoked, release-ready, or security-hardened unless those exact gates have evidence.
