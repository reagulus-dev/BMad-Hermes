# Pure Orchestrator Trigger / Worker Assignment Review Notes

Use when reviewing a story that implements a pure orchestrator evaluator for monitor events, worker assignment, idempotency, capacity gates, route health, or lock-aware selection without launching browsers/workers or wiring live Redis/DB/Electron runtime.

## Review stance

- Treat runtime QA as not applicable when the implementation is genuinely pure and does not add a live subscriber, DB write path, Electron surface, browser launch, checkout worker lifecycle, add-to-cart, payment, CAPTCHA/OTP/3DS/SCA, or final-submit behavior.
- Static validation should still include focused package tests, package typecheck/build, workspace typecheck/test where practical, and `git diff --check`.
- A workspace build failure caused by a known nested package-manager/Corepack wrapper issue can be recorded as tooling-only if the scoped package build and relevant workspace checks pass.

## Concrete blockers to check

### Reason-code specificity

If acceptance criteria require machine-readable reason codes, do not accept a generic `no_eligible_worker` for materially distinct safety outcomes.

Block when any required reason exists in the type union but is never returned, or when these outcomes collapse into a generic reason:

- all workers at capacity → should return `capacity_exceeded` or documented equivalent
- all profiles locked/unavailable → should return `locked_profile` or documented equivalent
- route unhealthy → should return route-specific reason
- duplicate/idempotency hit → should return duplicate/deduped-specific reason
- disabled target/group → should return disabled/not-active-specific reason

Reason-code granularity matters because future UI/history/runtime lifecycle stories consume these decisions.

### Profile uniqueness at the evaluator boundary

For checkout-worker assignment, profile-lock inspection is not the same as configuration uniqueness validation.

Block when:

- the story says assignment must respect profile uniqueness, but the evaluator only checks current lock status
- duplicate configured `profile_id` values among candidate workers can still produce an accepted assignment
- there is no focused test proving duplicate configured profiles are rejected or reason-coded before assignment

A passing correction should add an explicit duplicate-profile validation step before worker selection/assignment and a focused regression test.

## Suggested correction requirements after BLOCKED

- Add explicit reason-code behavior and tests for all-capacity and all-locked-profile cases.
- Add profile-configuration uniqueness validation before assignment.
- Add a focused test proving duplicate configured `profile_id` values cannot produce an accepted assignment.
- Re-run package tests/typecheck/build, workspace validation as practical, artifact parse checks when BMad files change, and `git diff --check`.
