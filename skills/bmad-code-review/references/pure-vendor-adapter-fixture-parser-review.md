# Pure Vendor Adapter / Fixture Parser Review Pattern

Use this reference when a BMad story implements a vendor-specific adapter contract or parser using offline fixtures only, without live browser/runtime wiring.

## Review stance

A pure vendor adapter/parser story can pass code review without Electron, Redis, DB, Playwright, or live vendor runtime QA when the story scope explicitly limits implementation to contracts + deterministic fixture parsing.

Use `PASS WITH NOTES` when:
- Public contracts are narrow and exported from the intended package boundary.
- The adapter entrypoint is pure and importable without browser/runtime/service dependencies.
- Fixture tests cover all acceptance states named by the story, including stock states, price reliability, guardrail signals, queue/session/failure states when implemented, and no-live-network behavior.
- The vendor module/registry marks only the implemented step as `implemented`; deferred add-to-cart/cart-review/checkout/verification steps remain placeholders.
- Generated renderer/static metadata is regenerated only to reflect registry state, not to introduce runtime behavior.

Use `BLOCKED` when:
- The adapter calls live vendor URLs or imports Playwright/Electron/Redis/DB/browser runtime despite a fixture-only scope.
- Marker/selector knowledge leaks into Electron, workflows, DB, shared config, or other non-vendor packages.
- Price handling lacks an explicit reliable vs unknown/unreliable distinction.
- Over-max/guardrail state is not explicit when reliable price exceeds max price.
- Tests only assert type imports or happy-path stock state and miss required failure/unknown/price/queue/session cases.
- The module registry claims later checkout/cart/verification steps are implemented without evidence.

## Evidence checklist

Inspect:
- Story artifact and dev record.
- Contract/types file and public exports.
- Parser implementation and import graph.
- Fixture tests and fixture content.
- Vendor registry/module step metadata.
- Generated renderer registry changes, if any.

Run or verify:
- Package typecheck/test/build for the vendor package.
- Relevant renderer tests if generated/static metadata changed.
- Workspace typecheck/test/build when story evidence requires it.
- `git diff --check` after review edits.
- A lightweight import/dependency search for forbidden runtime imports in the adapter package.

## Carry-forward notes to record

Even on pass, explicitly preserve:
- Live selector/page-content discovery remains unverified.
- Runtime browser/page capture remains future work.
- Redis/event publication, monitor UI, checkout-worker triggering, cart/checkout, payment, OTP, CAPTCHA, and 3DS/SCA remain out of scope unless separately implemented.
- Fixture marker strings may need tightening before live page-content use to avoid false positives from ordinary page chrome such as login/account links.

## Artifact/state pattern

After passing:
- Append findings to the story artifact under `## Review Findings`.
- Mark the reviewed story completed/review-passed in sprint status.
- Set QA/runtime verdict to an explicit not-applicable value for pure contract/parser scope.
- Advance live state only to the next story-creation boundary, not directly to implementation or release readiness.
