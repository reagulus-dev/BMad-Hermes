# HLX-5.3 AC1 Activation Gating Correction (2026-05-21)

Context:
- Story: HLX-5.3 — Build Checkout Workers UI and controls.
- AC1: Prevent saving or activating enabled workers when two enabled workers share one persistent profile reference.
- Initial review: BLOCKED because Start/activation remained enabled for an already-enabled worker whose profile was changed to conflict with another enabled worker.

Root cause:
- Save validation:
  - validateCheckoutWorkers(workers) detected duplicate enabled profile assignments and blocked Save.
- Start button logic:
  - Only checked:
    - worker not enabled
    - worker has no profileReference
  - Did NOT check whether the worker was part of a duplicate enabled profile assignment.
- So:
  - Editing an enabled worker to use another enabled worker’s profile:
    - Save was blocked, but
    - Start button still rendered as active.

Fix (bmad-dev-story correction):
- In nav-init.js:
  - workerDetail(workerId):
    - Use validateCheckoutWorkers(workers, includeDuplicateWorkerIds: true).
    - Mark isDuplicateProfileWorker(workerId) if:
      - worker is enabled and
      - present in duplicateWorkerIds.
    - Start button is now blocked when:
      - worker not enabled, or
      - no profileReference, or
      - isDuplicateProfileWorker(workerId).
  - Start click handler:
    - If blocked, show the one-worker-one-profile uniqueness message.

Test:
- In nav-init.test.ts:
  - AC1 regression test:
    - “blocks Start when two enabled workers share the same profile (activation gating)”.
    - Steps:
      - Set worker-2 to worker-1’s profile.
      - Open worker-2 detail via workerDetail(worker-2.id).
      - Confirm Start is aria-disabled=true.
      - Confirm alert text matches one-worker-one-profile invariant.

Lesson (class-level):
- When ACs say “prevent saving or activating” invalid entities:
  - Activation gating must use the same validation logic as save gating.
  - Do not rely only on duplicate-copy or disable-on-duplicate paths; also block activation for already-enabled entities whose configuration was edited into a conflicting state.
