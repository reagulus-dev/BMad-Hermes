# Worker-Owned Cart/Session State Model (HLX-5.4, 2026-05-21)

Canonical pattern for Helix: one worker ↔ one profile ↔ one cart/session.

## Core Rules

- Each checkout worker owns exactly one cart/session.
- Enforced via:
  - DB: unique constraint on worker_id in worker_cart_sessions.
  - Orchestrator: ownership guard before create/update.
- Sensitive data:
  - No raw credentials, cookies, tokens, OTP, payment details.
  - Represent as opaque/redacted references:
    - account_ref, shipping_ref, payment_ref.
- UI:
  - Display only:
    - Cart/session stage.
    - Target items and cart lines (safe metadata).
    - Guardrail status.
    - Opaque references (if present).
  - No hardcoded sensitive placeholders.

## DB Migration Pattern

- Table: worker_cart_sessions:
  - worker_id (PK, references checkout_workers(worker_id)).
  - checkout_stage (e.g., idle, reviewing, guarded).
  - guardrail_status (e.g., not_checked, passed, failed).
  - Attempt counts and lifecycle fields.
- UNIQUE constraint on worker_id ensures one cart/session per worker.

## Orchestrator Enforcement

- enforceWorkerCartSessionOwnership(workerId):
  - Validates worker_id exists.
  - Ensures no other worker uses the same cart/session.
- validateWorkerCartSessionCreate(workerId, payload):
  - Rejects if:
    - workerId unknown.
    - duplicate session exists.
    - payload contains raw secrets.
- validateWorkerCartSessionUpdate(workerId, payload):
  - Similar checks for updates.

## Test-Mode Gating

- Dev-only globals (e.g., __testSetCheckoutWorkerProfile):
  - Only exposed when an explicit test-mode flag is set (e.g., __HELIX_RENDERER_TEST_MODE__).
  - Not available in normal runtime behavior.
- Tests:
  - Enable the flag where needed.
  - Assert gating behavior in separate tests.

## References

- HLX-5.4 story artifact: _bmad/artifacts/stories/HLX-5.4-implement-worker-owned-cart-session-state-model.md
- DB migration: packages/db/migrations/006_worker_cart_sessions.sql
- Repository: packages/db/src/workerCartSessions.ts
- Orchestrator: apps/orchestrator/src/cartSessionOwnership.ts
