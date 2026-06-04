# Authorized Review Supersession Pattern — HLX-6.1 Add-to-Cart Boundary

Use this as a concrete example when a story has an already-committed `PASS WITH NOTES` review that the user later invalidates because it was run without authorization.

## Scenario

- Prior review commit existed and was already reflected in story/state/sprint/continuation artifacts.
- User explicitly said the prior review/QA notes were invalid and requested a fresh `bmad-code-review`.
- Implementation HEAD did not need to change; the review evidence and artifact anchors did.

## Review pattern

1. Treat the prior review as invalid progression evidence, even if its verdict is plausible.
2. Name the invalid commit in the new review section.
3. Re-review from repo truth, not from the invalid review notes.
4. If the story relies on an upstream/canonical boundary for an AC, rerun that boundary's focused tests too, not only the newly added story-local tests.
   - HLX-6.1 example: `runAtcBoundary()` delegated cross-profile/cart/vendor enforcement to `applyGroupingPolicyForUpsert()`.
   - Fresh review reran both `addToCartBoundary.test.ts` and `cartGrouping.test.ts` so AC1/AC4 evidence covered the delegated boundary.
5. Append a new `Fresh Authorized Code Review` section to the story artifact and update all evidence anchors to that section.
6. Reconcile `_bmad/state.json`, `_bmad/sprint-status.yaml`, and `CONTINUE-HERE.md` so future agents do not revive the invalid pass.
7. Parse JSON/YAML, run `git diff --check`, and commit the review/artifact updates separately.

## Classification guidance

- Missing story-local duplicate tests are not automatically blockers when the reviewed code path calls a canonical boundary that already has focused coverage and that coverage is rerun during review.
- Record this as a non-blocking note when direct assertions would improve local evidence but the actual enforcement path is correct and covered.
- Runtime/live checkout remains unclaimed unless live browser/vendor/Electron/Redis/DB-write evidence exists.
