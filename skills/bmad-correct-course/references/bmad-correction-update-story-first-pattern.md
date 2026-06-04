# Worked Example: Mid-Story Cleanup Correction (CF-E5-S3 Drop Legacy `CardItem.location`)

This is the worked example for the "Pre-Existing 'Preserve Legacy' Choices Often Deserve Reversal" section of `bmad-correct-course`. The user asked: *"Would it be cleaner if we remove legacy codes? No one uses the app yet apart from me."* The answer was yes, and the correction was performed as a `bmad-dev-story` correction on top of the same story (not a new `CF-E5-S4`).

## What the original story said

CF-E5-S3 added an additive `CardItemLocation` per-bin bucket model with a defensive scope item: *"Preserve the existing `CardItem.location` column during this story unless a migration-safe compatibility plan is explicitly implemented and tested."* The implementation honored that — both the column and the buckets were maintained, with a dual-write path in `setLocationForOwner` and a search-filter OR branch that matched both the column and the bucket.

## What the correction changed

A second `bmad-dev-story` pass (the cleanup correction) dropped the column entirely and simplified everything that had been dual-sourced:

| Surface | Before correction | After correction |
|---|---|---|
| `CardItem.location` column | preserved | dropped via new `20260602000001_drop_card_item_location_legacy` migration |
| `cardItemCreateSchema` / `cardItemUpdateSchema` | accepted `.location` | no longer accept it |
| `cardItemRepo.createForOwner` / `createManyForOwner` / `updateForOwner` / `bulkUpdateForOwner` | patch carried `.location` | `.location` removed |
| `listByOwnerFiltered` / `countByOwnerFiltered` search OR | matched `CardItem.location` AND `cardItemLocations` | bucket relation only |
| `setLocationForOwner` | smart find-update-delete-create with multi-branch logic | always `deleteMany` + `create` |
| `pendingCreates[]` in CSV import | carried `.location` | dropped; new parallel `pendingCreateLocations` array carries per-row bucket location |
| Edit / Create Card dialogs | text input for `location` | removed |
| InventoryTableClient location cell | read `item.location` | derived from `bucketSummaryByCardId` |

## The workflow rule the user asked for

> "Update the story before starting so that we avoid confusion."

This is now a hard rule in the skill. The artifact amendment was a single new section appended to the existing story:

```markdown
## Cleanup Correction — Drop Legacy `CardItem.location` Column

**Status**: supersedes the original scope item "Preserve the existing `CardItem.location` column".
**Initiated**: 2026-06-02 (post-dev-story, pre-code-review).
**Trigger**: founder is the only test user; the dual source-of-truth (legacy column + bucket table) adds two write paths and a search-filter branch for no production benefit.

### Updated scope (additive, then destructive)
1. **Schema** — drop `location String?` from `CardItem` ...
...
```

The amendment listed the new file paths, the acceptance criteria, the carry-forward notes, and the "Why this is the right call" rationale. The next agent reading the artifact sees: original implementation is documented, amendment supersedes one item, amendment validation summary, amendment carry-forward. No confusion.

## What the artifact amendment's acceptance criteria looked like

```markdown
### Acceptance criteria for the correction
- [ ] `prisma migrate diff` shows only the `DROP COLUMN` against the live schema.
- [ ] `CardItem` no longer has a `location` field in the generated Prisma client.
- [ ] `grep -r "CardItem\.location\|item\.location\|cardItem\.location\|card\.location" src/` returns no hits outside the migration comment and the schema integrity test's negative assertion.
- [ ] `pnpm prisma:validate`, `pnpm prisma:generate`, `pnpm typecheck`, `pnpm lint`, `pnpm test`, `pnpm build`, `git diff --check` all PASS.
- [ ] The 17 chaos-sort + 6 schema integrity + 11 S2 actions + 6 S1 csv-import + 355 total tests still pass with the legacy reads removed.
- [ ] No new Shopify, lot, sales, or analytics behavior is touched.
```

These criteria are the contract. They were checked in order before claiming done.

## The test updates that came with the correction

The 8 tests that needed touching were not new tests — they were existing tests whose `expect()` assertions still encoded the dual-source-of-truth world. The cleanup correction updated them in place, in the same commit as the code change:

- `cf-e5-s3-schema-migration.test.ts` (was 6, became 7): added a positive assertion that the cleanup migration drops the column, and a negative assertion that the schema no longer has the field.
- `cf-e5-s3-multi-location-stock.test.ts` (still 17): rewrote the `setLocationForOwner` "smart in-place update" tests to assert the simpler "always `deleteMany` + `create`" behavior; updated chaos-sort CSV merge/create assertions to drop the `location: "Bin A"` payload field and the `cardItem.update` call's `location` key.
- `owner-scope.production.test.ts`: rewrote `bulkUpdateForOwner` "applies `location: 'Binder B'`" test to use `archived: true`; updated `listByOwnerFiltered` search-OR test to drop the `CardItem.location` branch.
- `cf-e2-s2-stabilization.test.ts`, `inventory-actions-money.test.ts`, `cf-e5-s2-bulk-lot-assignment-actions.test.ts`: removed the `location` field from the test fixture payload and the expected `createForOwner` call.

Total test count stayed at **355/355** — no test was added, no test was deleted, every test that changed did so by in-place assertion update.

## The commit cadence

Two clean commits, code and docs split:

- `d8b606e refactor(CF-E5-S3): drop legacy free-text CardItem.location column` — 15 files, +185/-181, all code + tests + migrations.
- `32d4ae1 docs(CF-E5-S3): record cleanup-correction completion and reconcile state` — 4 files, +118/-19, all BMad artifacts.

The artifact updates never ride in the same commit as the code change, by the standard `bmad-dev-story` Artifact Update Sequence rule. The code commit is purely the code; the docs commit is purely the docs. They land in the same push, but the bisect is clean.

## The "do not reintroduce" carry-forward note

Added to both `sprint-status.yaml` and `state.json`:

> CF-E5-S3 cleanup correction (2026-06-02) dropped the legacy free-text `CardItem.location` column. `CardItemLocation` is the sole source of truth for physical storage location. Do not reintroduce the legacy column; do not add a `location` field to `CardItem` in any future story. If a new use case needs a non-bucket free-text on a card (e.g. a display label), it should live on `CardItem` as a different field (e.g. `displayLabel`) and not be confused with the per-bin bucket location.

This is the part a future agent actually needs. Without it, a later story could re-introduce a `location` field on `CardItem` thinking "the bucket model is for chaos-sort, but the legacy location is a useful display label," and the dual-source-of-truth would creep back in. The carry-forward names the *trap* and the *escape hatch* (different field name, different semantics).

## Why this isn't a `bmad-feature-retirement-clean-removal`

The field removal was scoped inside an active story; the story artifact was the anchor; one or two commits; same validation gates; the next workflow after correction is `bmad-code-review` for the same story. That is the `bmad-correct-course` shape. Feature retirement is for user-visible features that need installer / copy / route ceremony after the story is closed. Dropping a back-compat column on `CardItem` does not change user-visible behavior (the user already had to be on the new code path to interact with the data model), so the multi-step retirement ceremony would have been overhead.

## What this pattern protects against

- **Drift between the artifact and the code.** A future "what was the original scope?" question is answered by the artifact's superseded-amendment structure, not by re-reading the commit history.
- **Future agents adding the field back.** The carry-forward names the trap and gives a safe name (`displayLabel`) for any future free-text need that is genuinely different from the bucket location.
- **Premature abstraction for non-prod data.** The "preserve legacy" defensive default is right for a multi-tenant production app with live users. The user's context (solo founder, pre-launch) is a different default. Recording the decision and the conditions under which it would change is the durable lesson.
