# HLX-5.1: Orchestrator Trigger Evaluator and Worker Assignment

Date: 2026-05-20
Story: HLX-5.1 — Implement orchestrator trigger evaluation and worker assignment
Epic: Epic 5 — Checkout Worker Shell and Orchestration

## Context

This was the first Epic 5 story: introducing the orchestrator-side trigger evaluation and worker assignment logic without implementing checkout execution.

Key constraints:
- Pure evaluator (no Electron, no DB, no Redis, no browser).
- No add-to-cart, no cart review, no payment, no CAPTCHA/OTP/3DS/final-submit.
- Must integrate with:
  - HLX-2.5 (worker/profile model)
  - HLX-4.3 (monitor events)
  - HLX-TECHDEBT-2 (cleaned contracts)

## Implementation Pattern

- Created TriggerEventEvaluator in apps/orchestrator:
  - Accepts:
    - trigger event
    - monitor/task config
    - worker status
    - current assignments
  - Produces:
    - decision: assign_worker | skip | hold | fail
    - assigned_worker_id (when applicable)
    - reason_code
    - next_action_hint
  - Enforces:
    - max_concurrent checkouts
    - vendor-specific concurrency limits
    - cooldown/backoff windows
    - per-worker load limits
    - idempotency (no duplicate assignments)
    - lock-aware behavior (no conflict on locked tasks)

- Worker selection:
  - Deterministic policy:
    - prefer least-loaded, vendor-matched, non-cooldown workers.
  - Integrates with worker assignment, but not checkout execution.

- Task persistence record:
  - New TaskPersistenceRecord type for HLX-5.2 wiring:
    - task_id, monitor_id, vendor, item, trigger_ts, assignment_id, worker_id, status, reason_code, etc.

## Validation

- pnpm -r run typecheck: PASS
- pnpm -r run test: PASS (19/19 orchestrator tests)
- git diff --check: PASS
- Commit: 9cb0827 feat(HLX-5.1)
- Runtime claims:
  - Not claimed (no Redis, no live desktop/Discord, no human visual QA).
  - Pre-existing build issue in apps/desktop-electron (Corepack shim) documented as out of scope.

## Lessons

- For orchestration/worker-assignment stories:
  - Keep the evaluator pure and policy-focused; defer runtime wiring to follow-up stories.
  - Define TaskPersistenceRecord now so the next story can wire it to DB/Redis without re-design.
  - Be explicit: “assignment is not execution” — do not let the story drift into implementing checkout steps.
  - Do not block completion on a pre-existing build failure in an unrelated workspace; document and continue.
