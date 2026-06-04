# CardForge multi-bucket editor + runtime-smoke review pitfall

Use this reference when reviewing CardForge stories that add or polish a manual multi-bucket `CardItemLocation` editor, especially CF-E5-S4-style finish-gate stories that claim runtime QA and Supabase deployment.

## Key lesson

Client-side bucket-total validation is not enough. If the story requires an editor to enforce `sum(bucket.quantity) == CardItem.quantity`, the server/repository replacement boundary must enforce the invariant before deleting/replacing bucket rows.

A passing focused test suite can still miss this if tests only assert schema shape and helper-call delegation.

## Blocker pattern 1: replacement helper does not verify total against CardItem.quantity

Block when:

- The UI computes `total === item.quantity` and disables Save, but
- The server action accepts JSON bucket rows and delegates to a repository helper, and
- The helper only checks ownership with `select: { id: true }` (or equivalent), then deletes existing buckets and creates the supplied list, and
- The helper never selects `CardItem.quantity`, computes the submitted bucket sum, or rejects mismatches.

Concrete risk:

- A malformed, stale, or manual request can replace a positive-quantity card's buckets with an empty list or mismatched totals.
- The source may contain misleading comments that say the helper enforces the invariant while it actually delegates only schema/ownership checks.

Required correction:

- In the replacement helper, select the owned card's `quantity`.
- Compute `bucketSum = sum(submitted.quantity)` before the destructive transaction.
- Reject unless `bucketSum === card.quantity`.
- Add focused regression tests for:
  - mismatched submitted total vs card quantity,
  - empty bucket list for a positive-quantity card,
  - valid multi-bucket list still replacing successfully.

## Blocker pattern 2: finish-gate runtime-smoke ACs are overclaimed

For finish-gate stories whose scope explicitly says runtime/founder QA or current-feature runtime smoke is part of the story, do not downgrade missing runtime evidence to a note merely because source/static validation passes.

Block when the story AC requires runtime evidence for authenticated/dev-owner inventory flows, but the recorded evidence only proves:

- dev server starts/compiles,
- `/login` renders,
- unauthenticated `/inventory` redirects to `/login`.

Those checks are useful but do not prove:

- authenticated inventory page load or documented dev-owner setup,
- location filter/search behavior,
- multi-bucket edit/save validation in the running app,
- representative CSV/import route/action boundary,
- manual create/update quantity or sale deduct/restore surfaces where reachable.

Required correction:

- Run and record an authenticated/dev-owner runtime smoke for the story-named flows, or
- Formally re-scope the story/ACs before fresh review so code review is not forced to accept missing story-required evidence.

## Non-blocking deployment note

Secret-safe live Supabase evidence that verifies target tables, removed legacy columns, indexes/FKs, policy presence, and migration-history reconciliation can be accepted with notes even when a superseded migration is intentionally not backfilled, as long as the story/artifacts explicitly explain why the migration is superseded and must not be applied.
