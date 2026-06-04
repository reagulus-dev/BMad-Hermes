# Renderer Control Activation Gating Review

Use this reference when reviewing Electron/static-renderer control surfaces where the story acceptance criteria require preventing invalid runtime actions (for example checkout-worker Start/Warm/Pause controls) even if the controls are currently representational.

## Pattern

A UI may correctly validate an invalid configuration on Save while still exposing an activation/control button that acts as if the invalid configuration is usable. If the AC says the UI must prevent saving **or activating** invalid entities, the review must inspect both paths:

- Save/configuration validation path.
- Control/activation gating path in the rendered detail/list UI.
- Focused tests that open the affected rendered entity and assert the control is disabled or clearly blocked.

## Checkout-worker example

For one worker ↔ one profile ↔ one cart/session invariants:

- Duplicate enabled profile assignment detection on Save is necessary but not sufficient.
- Start/activation must also be blocked when the selected enabled worker participates in a duplicate enabled profile assignment.
- A copied/duplicated worker that clears `profileReference` and disables itself can pass the duplicate-copy path, while an existing enabled worker edited to share another enabled worker's profile can still be a blocker if Start remains enabled.

## Review stance

Use `BLOCKED` when an explicit AC requires preventing activation and the rendered control remains enabled for an invalid entity, even if:

- Workspace validation passes.
- Save-path validation displays an error.
- Other ACs pass.
- Runtime bridge is intentionally deferred and controls are representational.

Use `PASS WITH NOTES` only when activation controls are correctly gated and the remaining limitation is just that the controls are not wired to live runtime behavior, with no claim that they are.

## Correction expectation

The correction should:

1. Compute whether the current entity participates in the invalid duplicate/conflict condition.
2. Include that condition in the Start/activation disabled state and operator copy.
3. Add a focused renderer regression test that creates or selects the invalid entity and proves the control is blocked.
4. Re-run focused tests plus workspace validation before a fresh review.
