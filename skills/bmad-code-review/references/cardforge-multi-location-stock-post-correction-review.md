# CardForge multi-location stock post-correction review pattern

Use this reference when re-reviewing CF-E5-S3-style inventory/location-bucket stories after an initial BLOCKED review and a correction commit.

## Key lesson

A correction can fully resolve the named prior blockers while still leaving broader story-level invariants broken. Do not limit the fresh review to only the previous blocker list when the story's acceptance criteria define a wider consistency boundary.

For CardForge-style `CardItem.quantity` + `CardItemLocation` bucket models, review every production path that can create or mutate quantity, not only the CSV/import path that was just corrected.

## Blocker patterns found after a correction

### 1. Same-batch new identities in CSV merge mode

If duplicate detection is built only from pre-existing DB rows, then merge mode may still duplicate logical card identities that appear twice for the first time in the same CSV import.

Check for:

- `existingByIdentity` or equivalent built only from `cardItemRepo.listByOwner(ownerId)` before import.
- No `pendingByIdentity` / same-batch accumulator for new rows.
- `duplicateMode === "merge"` coalesces only pre-existing identities.

Block when two new same-identity rows at different locations would become two `CardItem` rows instead of one `CardItem` with multiple buckets.

Require focused regression coverage:

- merge mode
- no pre-existing cards
- two same logical identities in the same CSV
- distinct locations
- expected: one logical card create/update and multiple buckets whose total equals quantity

### 2. Non-atomic create-with-buckets path

A merge helper that updates `CardItem.quantity` and replaces buckets in one transaction does not prove the create path is safe.

Block when code does:

1. `createManyForOwner(...)` or `createForOwner(...)` for `CardItem`
2. later re-fetches created cards
3. creates `CardItemLocation` buckets one-by-one outside the same transaction

This can leave `CardItem.quantity > 0` with no matching buckets if bucket creation fails.

Prefer an owner-scoped repo/service helper that creates a card and its initial buckets in one transaction, or a bulk create boundary that returns deterministic created IDs and writes all buckets atomically.

### 3. Ambiguous bucket matching for duplicate created signatures

If create-mode allows duplicate logical identities, re-fetch matching with a `Set` of signatures and `findIndex(...)` can assign the wrong pending row's location to multiple created cards.

Block when row-to-created-card mapping loses multiplicity/order and bucket locations are derived from the first matching pending row.

Require tests for duplicate create-mode rows with the same identity and different locations, proving each created card gets the correct matching single bucket.

### 4. Manual inventory and sales quantity paths

When `CardItemLocation` becomes the sole location source of truth and `CardItem.quantity` remains the canonical total, audit all non-import quantity paths:

- manual inventory create actions
- manual inventory quantity edit actions
- sale create/update/delete status transitions that decrement/restore inventory
- bulk location assignment or collapse actions

Block if any production path can change `CardItem.quantity` without creating/reconciling bucket totals, unless the story explicitly scopes and labels that path as intentionally not bucket-aware and the acceptance criteria permit it.

For CardForge CF-E5-S3, manual sales/inventory behavior was an explicit AC, so stale bucket totals from manual create/update or sales decrement/restore were blockers.

### 5. Filtered summary buckets must be narrowed to filtered items

A bucket-derived summary can still be wrong if the bucket list is unfiltered.

Check whether the page fetches both `allBuckets` and `filteredBuckets` with the same unfiltered `listForOwner(ownerId)` call. If `buildInventorySummary(filteredItems, filteredBuckets)` counts locations from the full owner bucket list, filtered location counts are false.

Require either:

- narrow buckets to `filteredItems.map(id)` before summary calculation, or
- add a repo helper that fetches buckets for the filtered card set.

Add a focused test proving filtered Locations summary excludes buckets for non-matching cards.

## Review stance

- Passing focused/full validation is not enough if tests do not exercise the invariant-breaking paths.
- Fresh post-correction review should explicitly list which prior blockers are resolved, then separately audit remaining story ACs/invariants.
- Independent focused subagent review can be useful, but verify every subagent finding against source before recording the verdict.
