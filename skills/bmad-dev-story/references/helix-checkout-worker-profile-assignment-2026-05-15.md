# Helix checkout-worker profile assignment validation pattern — 2026-05-15

## Context
HLX-2.5 implemented a configuration/runtime guard for the product rule: one checkout worker owns exactly one unique browser profile/cart/session.

## Reusable pattern
For configuration stories that assign scarce runtime resources (profiles, accounts, carts, routes, devices, seats) to workers:

1. Add a typed assignment model using opaque references, not raw secrets or storage paths.
2. Add a pure validation function that returns structured issues for UI save-time blocking.
3. Add an assert/guard wrapper for runtime startup so stale/imported config cannot bypass UI validation.
4. Add duplicate/copy helpers that clear the scarce-resource assignment and disable the duplicate until an operator chooses a new unique resource.
5. Centralize the product-rule error copy so UI and runtime failures explain the same invariant.
6. Cover both paths in tests:
   - valid unique assignment passes
   - duplicate enabled assignment fails
   - missing required assignment fails
   - runtime assertion throws before execution
   - duplicate/copy clears the assignment
   - renderer/UI save path shows blocking copy

## Evidence boundary
A JSDOM test against the actual static renderer script can prove shell UI validation behavior, but it is not full Electron graphical runtime verification. Report it as static renderer/runtime-script evidence unless an Electron click-through smoke is run.

## Example invariant copy
`Each checkout worker must use a unique profile: one worker ↔ one profile ↔ one cart/session.`

## Files from the Helix instance
- `packages/config/src/index.ts`
- `packages/config/src/index.test.ts`
- `apps/desktop-electron/src/renderer/nav-init.js`
- `apps/desktop-electron/src/renderer/nav-init.test.ts`
- `_bmad/artifacts/evidence/HLX-2.5-checkout-worker-profile-assignment-2026-05-15.md`
