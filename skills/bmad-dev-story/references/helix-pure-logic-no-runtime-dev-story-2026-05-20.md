# Pure Logic + Tests, No Runtime Dev-Story Pattern (HLX-5.2)

## Context

Some BMad dev stories are:
- Pure internal logic (state machines, validators, policies, domain rules).
- Fully testable with unit tests.
- Not yet wired to runtime, UI, or external services.
- Explicitly out-of-scope for:
  - Electron/runtime UI
  - Browser automation
  - Live Redis/PostgreSQL use
  - Vendor/checkout/3DS/SCA/OTP flows

Example: HLX-5.2 (checkout worker lifecycle state machine).

## Pattern

For these stories:

- Treat the story as:
  - implementation: types, classes, pure functions
  - validation: typecheck, unit tests, build
  - no runtime claims

- Explicit rules:
  - Do not:
    - Claim runtime-verified
    - Claim live-integration verified
    - Claim founder-review ready
    - Pretend the component is wired into Electron/worker/browser
  - Do:
    - Run:
      - pnpm -r run typecheck
      - pnpm -r run test
      - pnpm -r run build
    - Add focused unit tests:
      - Normal flows
      - Edge cases
      - Invalid/unknown inputs
      - Terminal states and no-op behavior
    - Clearly mark runtime/UI/worker/vendor/checkout integration as “out of scope” or “deferred.”

- Artifact updates:
  - state.json:
    - current_story: HLX-5.2
    - workflow_status: implemented_not_reviewed
    - next_recommended_workflows: bmad-code-review for HLX-5.2
  - sprint-status.yaml:
    - HLX-5.2: implemented_not_reviewed
  - CONTINUE-HERE.md:
    - Update current status to “dev story complete, awaiting bmad-code-review.”
    - Note: no runtime/UI/worker/vendor behavior implemented.

Use this pattern whenever a story is strictly internal logic with no runtime wiring.
