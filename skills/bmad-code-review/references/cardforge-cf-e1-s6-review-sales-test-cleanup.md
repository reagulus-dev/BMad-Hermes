# CardForge CF-E1-S6 review: unrelated failing test becomes safe cleanup

Use this as a concrete pattern when a story review repeatedly carries a known unrelated failing test, and the user asks the reviewer to "have a look" while doing the fresh review.

## Situation

- Story under review: CardForge `CF-E1-S6` analytics/HMRC export.
- Prior validation carried a single unrelated failure: `tests/unit/sales-service.test.ts:446`.
- Failure text showed a stale assertion message only:
  - Expected regex: `/exceeds effective available quantity/`
  - Actual implementation error: `Sale quantity (6) exceeds available quantity (5)`
- Source behavior was already correct: same-card update with current card quantity 4 and existing sale quantity 1 computes effective availability 5 and rejects requested quantity 6.

## Review-safe handling

When the user explicitly asks to inspect the known unrelated failure during code review:

1. Reproduce the focused failing test first.
2. Inspect the source behavior around the assertion before editing.
3. If the implementation behavior is correct and only the assertion wording is stale, patch the test expectation as a tiny reviewer cleanup.
4. Rerun:
   - the focused formerly failing test file,
   - the story-focused tests,
   - the full validation bundle if the cleanup removes the only known full-suite failure.
5. In the review finding, explicitly classify the edit as assertion-message cleanup only, not product behavior change.
6. Reconcile the story/state/sprint/continuation artifacts so the old "known unrelated failure" note is removed and full-suite validation records the new all-green count.

## Evidence pattern from the session

- Focused combined tests: `corepack pnpm exec vitest run tests/unit/sales-service.test.ts tests/unit/analytics-and-exports.test.ts --reporter=dot` → 56/56 PASS.
- Full suite: `corepack pnpm test` → 177/177 PASS.
- Static/build bundle also passed: lint, typecheck, Prisma validate with redacted dummy `DATABASE_URL`, build, `git diff --check`.

## Pitfall

Do not keep carrying a "known unrelated failing test" note after the failure has been safely fixed. Update all BMad layers and continuation docs to remove the stale failure language, otherwise the next state-check may under-trust an actually clean repo.
