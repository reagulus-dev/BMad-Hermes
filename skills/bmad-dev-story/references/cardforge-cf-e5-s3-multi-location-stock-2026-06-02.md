# CF-E5-S3 — Multi-Location Stock Model (Option C) (2026-06-02)

CardForge story that landed clean (373/373 tests after three corrections, all validation gates pass, additive Prisma schema change with migration backfill, a same-day bounded cleanup correction that dropped the legacy `CardItem.location` column, a same-day first-round `bmad-dev-story` correction that resolved three review blockers (sort column allowlist, language/finish persistence, atomic merge), a same-day second-round `bmad-dev-story` correction that resolved four more review blockers (same-batch new-identity CSV merge coalescing, atomic CSV create-with-buckets, manual + sales bucket-total alignment, filtered Locations summary narrowing), and a same-day third-round `bmad-dev-story` correction that resolved the two remaining no-bucket invariant edges (CSV merge into a no-bucket positive-quantity card, sales partial deduct from a no-bucket positive-quantity card). The implementation surfaced patterns that recur in any "additive multi-row child model with composite owner-consistent relation + chaos-sort CSV import + bulk UI action" story; the cleanup correction surfaced patterns for "defensive preserve-legacy defaults that no longer match the project context"; the three correction rounds surfaced patterns for "invariants partially enforced at one layer but not at the boundary that actually mattered," "re-running a bmad-dev-story correction after the first review round still leaves invariants un-fixed in adjacent write paths," and "even after walking every boundary, the boundary-walk itself can miss a path when the path's no-bucket / no-rows / no-presence shape is a corner of the input space, not a common case."

## Reusable patterns (any project)

### 1. Additive per-row child model: enforce the bucket invariant at every write boundary

When a story adds a new child model (e.g. `CardItemLocation` buckets) that must stay consistent with a parent total (e.g. `CardItem.quantity`), pick the invariant explicitly and enforce it at **every** write path that touches either side. The invariant for this story:

```text
sum(CardItemLocation.quantity WHERE card_item_id = X) == CardItem.quantity for that card
```

Write boundaries that all had to enforce it:

1. **Migration backfill** — inserts one bucket per `quantity > 0` parent row with `bucket.quantity = parent.quantity`.
2. **Bulk action repo helper** (e.g. `setLocationForOwner`) — `prisma.$transaction` with `updateMany` on parent + `deleteMany` + `createMany` on child so the bucket set is never partial.
3. **CSV import merge path** — accumulates per-bin mutations across rows for the same parent id and atomically replaces the bucket set after the row loop so the parent total and the child total stay aligned.

The third one is easy to miss: if you re-snapshot the original bucket list on every row, multi-row CSV imports silently lose deltas. Always re-read from the in-progress map.

### 2. Vitest `$transaction` mock pattern for production code

Production code that uses `prisma.$transaction(async (tx) => { ... })` needs a specific mock implementation in tests, not a bare `vi.fn()`. The repo's prisma is mocked at the module boundary, so the `tx` parameter received by the callback is the same mocked object — wire the mock to run the callback against the mocked prisma:

```ts
vi.mock("@/lib/db/prisma", () => {
  const mockPrisma = { /* ... */ };
  mockPrisma.$transaction = vi.fn();
  return { prisma: mockPrisma };
});

// inside a test:
mockPrisma.$transaction.mockImplementation(
  async (fn) => fn(mockPrisma)
);
```

Without `mockImplementation`, `$transaction` returns `undefined` and the inner `tx.cardItemLocation.deleteMany` / `tx.cardItemLocation.createMany` calls never reach the mocked functions, so the production logic appears to silently no-op.

### 3. `cardItemRepo.updateForOwner` uses singular `update`, not `updateMany`

CardForge's `cardItemRepo.updateForOwner(id, ownerId, patch)` performs an ownership check via `findFirst` then writes with `prisma.cardItem.update({ where: { id }, data })` (singular). When asserting calls from action-layer code, use:

```ts
expect(prisma.cardItem.update).toHaveBeenCalledWith({
  where: { id: 100 },
  data: { quantity: 5 },
});
```

`prisma.cardItem.updateMany` is reserved for true bulk operations (e.g. `assignLotForOwner`, `unassignLotForOwner`, `bulkUpdateForOwner`, `setLocationForOwner`).

### 4. Chaos-sort merge accumulation across rows

For CSV import where the same logical identity may appear in N rows at different physical locations, accumulate mutations in a per-parent map and re-read from that map (not from the original snapshot) on each row:

```ts
let merged = pendingBucketMerges.get(parentId);
if (!merged) {
  // first row for this parent — snapshot from the original bucket list
  merged = originalBucketsByParent.get(parentId) ?? [];
}
const idx = merged.findIndex((b) => b.location === location);
if (idx >= 0) merged[idx].quantity += row.quantity;
else merged.push({ location, quantity: row.quantity });
pendingBucketMerges.set(parentId, merged);
```

Apply mutations per-parent after the row loop completes (not per-row), inside `replaceBucketsForCardItem` so the bucket set is atomic.

### 5. Chaos-sort identity key: include all "logical identity" fields, not just name+set

For chaos-sorted imports, the dedup key must include every field that defines the logical card identity. For Pokemon TCG that is:

- `name` (trimmed, lowercased)
- `set_code` (and/or `set_name` if used)
- `card_number`
- `condition` (NM/EX/...)
- `language` (EN/JP/...)
- `finish_type` (REGULAR/REVERSE_HOLO/...)

Leaving out `language` or `finish_type` causes a JP Regular and an EN Reverse Holo of the same `name/set/number/condition` to be wrongly merged. This is a behavior change for any pre-existing chaos-sort CSV that mixed languages / finishes, so document the change in the story artifact's Dev Agent Record and call it out as a key decision.

### 6. Composite owner-consistent Prisma relation: declare it in the schema, not just the migration

When the new child model must be owner-consistent with the parent, declare the relation in `schema.prisma` with the composite key (not just at the SQL migration level):

```prisma
model CardItemLocation {
  id             Int      @id @default(autoincrement())
  owner_id       Int
  card_item_id   Int
  // ... other fields

  cardItem       CardItem @relation(
    fields: [card_item_id, owner_id],
    references: [id, owner_id],
    onDelete: Cascade
  )

  @@unique([id, owner_id])
}
```

Prisma's `@@unique([id, owner_id])` is required so the `cardItem_id, owner_id -> id, owner_id` composite FK is even possible. The corresponding SQL migration also adds the composite FK constraint and enables RLS so cross-owner references are blocked at the DB layer too.

### 7. Additive migration: backfill in the same migration, not a separate one

When the story is "add a derived per-row child model and backfill from existing parent data," do the backfill INSERT in the same migration file as the CREATE TABLE. Splitting it across two migrations creates a window where the child table exists but is empty, which is observable to running app instances if `prisma migrate deploy` runs them out of order. One migration, one transaction, atomic.

### 8. Parallel-array pattern: capture per-row data when the persistent model has no corresponding field

When the persistent model doesn't carry the field (e.g. `CardItem.location` was dropped in the cleanup correction, but the CSV import still needs the per-row location string to write to the bucket table), do not shove the value onto the persisted row. Use a parallel array indexed by the persistent array:

```ts
const pendingCreates: CreateInput[] = [];
const pendingCreateLocations: { index: number; location: string | null }[] = [];

for (const row of importableRows) {
  const location = row.location?.trim() || null;
  // ... duplicate detection ...
  pendingCreateLocations.push({ index: pendingCreates.length, location });
  pendingCreates.push({ name, setName, /* ...no location... */ });
}

// after createMany, walk the new rows and write a matching bucket per row,
// looking up the location by index:
for (const i = 0; i < afterCreates.length; i++) {
  const card = afterCreates[i];
  const myLocation = pendingCreateLocations.find((p) => p.index === i)?.location;
  await cardItemLocationRepo.createForOwner(ownerId, {
    cardItemId: card.id,
    location: myLocation ?? null,
    quantity: card.quantity,
  });
}
```

The alternative — `createMany` with `select: { id: true }` to learn the new ids and then zip back by index — fails for `createMany` because Prisma does not return the new ids by default. The parallel array survives that limitation and stays O(N) in the test mock by not needing the production `findMany` re-read. (The CardForge CSV import does re-read the new rows from the DB to discover which `pendingCreates` row each returned `id` corresponds to; that is the existing pattern from before S3 and it works fine for ≤ 10k-row imports.)

### 9. Bucket-rewrite helper: prefer always-deleteMany-then-create over smart find-update

When a "set the bucket set for this card to exactly N bins" helper would otherwise branch into "find the matching bucket, update its quantity, leave the others alone; if no match, find a target bucket to update, otherwise delete and create," the simpler shape is always correct:

```ts
// in $transaction:
for (const card of owned) {
  await tx.cardItemLocation.deleteMany({
    where: { owner_id: oid, card_item_id: card.id },
  });
  await tx.cardItemLocation.create({
    data: { owner_id: oid, card_item_id: card.id, location, quantity: card.quantity },
  });
}
```

The smart-bucket path was the original CF-E5-S3 implementation; the cleanup correction simplified it. The simpler shape is correct because:

- The invariant `sum(buckets) == CardItem.quantity` is preserved either way (the new bucket always carries the full quantity).
- The test surface shrinks from "find-update-delete-create" with three branchy paths to "deleteMany + create" with two linear calls.
- The "smart" path silently allowed the bucket count to drift from the persisted CardItem.quantity when cost-basis corrections or other partial updates happened; the simple path always reconciles.

If a future story needs partial bucket updates (e.g. "shift 3 units from Bin A to Bin B"), it should be a **new** repo helper (`transferQuantityBetweenBucketsForOwner`) that operates on the existing buckets, not a more-branched `setLocationForOwner`.

## CardForge-specific (do not silently change)

- **`CardItemLocation` is the sole source of truth for physical storage location** as of the CF-E5-S3 cleanup correction (2026-06-02). The legacy free-text `CardItem.location` column was dropped via `20260602000001_drop_card_item_location_legacy`. Do not reintroduce the column. If a future use case needs a non-bucket free-text on a card (e.g. a display label), it should live on `CardItem` as a different field (e.g. `displayLabel`) — see the carry-forward note in `sprint-status.yaml` and `state.json`.
- **Bulk "Apply" location control in the inventory table still takes a single string** and collapses any existing buckets at a non-target location via the simplified `setLocationForOwner` (always `deleteMany` + `create`). Full per-bin multi-bucket editor UX is out of scope for this story; document the follow-up in CONTINUE-HERE.md and `sprint-status.yaml` carry-forward concerns.
- **CF-E5-S2 cost-basis contract is unchanged.** `assignLotForOwner` still computes `Math.max(1, Math.round(lot.total_cost_pence / selectedTotalQuantity))` and writes `lotId` + `cost_basis_pence` in a single `updateMany`. No regression.
- **CF-E5-S2 `__none` sentinel for `Lot: Unassigned` is unchanged.** Never overload numeric 0.

## Story metadata

- Story: `_bmad/artifacts/stories/CF-E5-S3-multi-location-stock-model-option-c.md`
- Migrations: `prisma/migrations/20260602000000_add_card_item_locations/migration.sql` (additive + backfill), `prisma/migrations/20260602000001_drop_card_item_location_legacy/migration.sql` (cleanup correction drops the legacy column)
- New tests: 30 (17 chaos-sort + owner-scope + repo, 7 schema/migration integrity, +6 from the first-round bmad-dev-story correction: 2 for location sort removal, 3 for the atomic merge helper, 1 for CSV create-mode language/finish persistence) + 9 from the second-round bmad-dev-story correction: 4 for the atomic create-with-initial-buckets helper (boundary, duplicate-row pairing, pre-flight guard, batch rollback), 3 for `updateQuantityForOwner` (rebalance, delete-on-zero, null-bucket creation), 2 for sales deduct/restore bucket alignment + 3 from the third-round bmad-dev-story correction: 1 for CSV merge into a no-bucket positive-quantity card (null-location seed + new Bin A bucket, sum invariant), 1 for CSV merge into a no-bucket card with a null-location incoming row (single merged null-location bucket), 1 for sales partial deduct on a no-bucket positive-quantity card (single null-location bucket equal to post-deduct quantity, in-memory harness with `Map<cardItemId, Map<bucketId, { location, quantity }>>`)
- Suite trajectory: 332 (pre-S3) → 355 (S3 + cleanup correction) → 361 (S3 first-round bmad-dev-story correction) → 370 (S3 second-round bmad-dev-story correction) → 373 (S3 third-round bmad-dev-story correction)
- Status: `implemented_not_reviewed` (after third-round correction), awaiting fresh `bmad-code-review` after the third correction landed

## Why the cleanup correction superseded the "preserve legacy" default

The original story's "preserve the legacy `CardItem.location` column" scope item was correct as a defensive default for a multi-tenant production app with live users. The founder later confirmed they are the only test user (pre-launch, no production data, no migration to defend against). At that point the dual source-of-truth became pure complexity cost:

- Two write paths (the column and the buckets)
- A search-filter OR clause matching both
- A search-filter branch in `setLocationForOwner`'s smart update
- A schema integrity concern about what the legacy column "really" means

Dropping the column was a single new migration + a single repo simplification + a single carry-forward line. The cost of preserving the column was ongoing, the cost of dropping it was bounded. The cleanup-correction pattern is now documented in `bmad-correct-course` under "Pre-Existing 'Preserve Legacy' Choices Often Deserve Reversal" for the next agent that faces the same default-vs-context question.

## Patterns from the bmad-dev-story correction (2026-06-02) — first round

The first code review on this story returned `BLOCKED` on three points: (1) the inventory `sortBy=location` clause still targeted the removed `CardItem.location` Prisma field, (2) the CSV identity key included `language` and `finish_type` but the create-mode `pendingCreates` payload omitted them, (3) the merge-mode `CardItem.quantity` update and the bucket replacement ran as two separate non-transactional calls. All three had the same shape: an invariant or constraint that was partially enforced at one layer (schema, action, repo) but not at the boundary that actually mattered. The correction introduced four patterns that are reusable for any "additive multi-row child model with composite owner-consistent relation + chaos-sort CSV import" story, including future CF-E5 stories and the planned `CF-E5-S4` multi-bucket editor.

### 10. Defense-in-depth allowlist at the repo layer for `orderBy` / `sortBy` fields

When a Prisma column is removed from the schema, every call site that maps a request field to that Prisma column must be updated. The schema layer is the first defense (Zod enum restricts the field), but a hand-crafted request or a future regression can still pass an unknown `sortBy` to the repo. The repo is the second defense.

**Pattern**: in any `listByOwnerFiltered`-style helper that maps `filters.sortBy` to Prisma `orderBy`, declare an allowlist `Set` of valid Prisma field names and silently drop any unknown `sortBy` to the safe default sort. Never throw — a bad request is a UX issue, not a 500.

```ts
const ORDER_BY_ALLOWLIST = new Set([
  "name", "set_name", "condition", "cost_basis_pence",
  "quantity", "status", "created_at", "sort_order",
] as const);
const orderBy: Record<string, "asc" | "desc">[] = [];
if (filters.sortBy && ORDER_BY_ALLOWLIST.has(filters.sortBy as never)) {
  orderBy.push({ [filters.sortBy]: filters.sortDir ?? "asc" });
} else {
  orderBy.push({ sort_order: "asc" });
  orderBy.push({ created_at: "desc" });
}
```

**Test**: assert that a hand-crafted `sortBy: "removedField"` falls back to the default `orderBy` and never passes the unknown field to Prisma. This is the regression that catches "we forgot to update the allowlist when we removed a column."

**Generalization**: applies to any `orderBy`, `select`, `include`, or any other Prisma field that the user can influence. A whitelist at the repo boundary plus a parse-time enum at the schema layer is the correct two-layer defense.

### 11. Atomic stock-mutation helper as a repo-layer boundary, with a pre-flight invariant guard

When a user action must mutate a parent total AND a child breakdown together (e.g. `CardItem.quantity` and `CardItemLocation` buckets), the atomicity boundary belongs at the **repo layer**, not the action layer. An action that calls two separate repo methods cannot enforce atomicity — the second call can fail and leave the parent total and the child total out of sync.

**Pattern**: add a single repo helper whose signature is the entire mutation:

```ts
applyMergeStockForOwner: async (
  ownerId: OwnerId,
  cardItemId: number,
  payload: { quantity: number; buckets: { location: string | null; quantity: number }[] }
) => {
  // 1. Validate inputs at the boundary.
  // 2. Pre-flight invariant guard: reject if sum(buckets) !== quantity.
  // 3. Verify ownership with findFirst.
  // 4. Open a single prisma.$transaction:
  //    - cardItem.update({ where: { id }, data: { quantity } })
  //    - cardItemLocation.deleteMany(...)
  //    - cardItemLocation.createMany(...)
  // 5. Return the new state.
};
```

The pre-flight invariant guard (`sum(buckets) !== quantity` → throw before opening the transaction) is critical: it catches malformed caller payloads at the boundary, before any database work happens. A future caller that constructs `{ quantity, buckets }` inconsistently fails fast with a clear error instead of leaving the database in a broken state.

The action layer becomes a one-liner per affected card:

```ts
for (const [id, quantity] of mergeQuantities) {
  await cardItemRepo.applyMergeStockForOwner(ownerId, id, { quantity, buckets: ... });
}
```

**Tests** (all required to lock the contract):

- The pre-flight invariant guard rejects with a clear error when `sum(buckets) !== quantity` and never opens a `$transaction`.
- The single-transaction shape: ownership check + quantity update + bucket replace all happen inside ONE `prisma.$transaction` call (assert `$transaction` was called exactly once).
- The rollback shape: when the bucket createMany fails inside the `tx`, the error propagates and the quantity update is discarded (Prisma rolls back the entire transaction). Assert the error message and that the call shape is still one `$transaction`.

**Generalization**: applies to any "update parent + replace child set" write path that must be atomic. Other examples: `updateSaleWithAllocations` (sale total + per-line allocations), `reorderLotItems` (lot total + per-card reorder), `reassignExpenseCategory` (expense + per-transaction tag set).

### 12. Normalize free-form CSV strings to Prisma enums with explicit `OTHER` fallback

When a CSV import accepts free-form strings for an enum field (e.g. `language: z.string().optional()`), the row's `language` must be normalized to the Prisma enum before being persisted. The naive pattern `row.language || "EN"` has two bugs:

1. The string is not typed as the enum, so it doesn't satisfy `CardItemWriteForOwner.language: CardLanguage | undefined` (typecheck fails).
2. The fallback is silent: a free-form string like `"chinese"` is coerced to `"EN"` by the time it reaches the persisted row, which silently disagrees with the row's identity key.

**Pattern**: a small `parseEnum` helper per enum field that case-insensitive-matches the enum, returns the default for `undefined`, and returns the explicit `OTHER` value for unknown strings. The enum must include an `OTHER` value (it does in the CardForge `CardLanguage` and `CardFinishType` enums).

```ts
function parseLanguage(raw: string | undefined): CardLanguage {
  if (!raw) return CardLanguage.EN;
  const upper = raw.toUpperCase().trim();
  if ((Object.values(CardLanguage) as string[]).includes(upper)) return upper as CardLanguage;
  return CardLanguage.OTHER;
}
```

The action layer uses the parsed enum value everywhere — identity key, persisted `pendingCreates` payload, and any test that asserts the createMany call shape.

**Test**: import a CSV row with non-default values (e.g. `language=JP, finishType=REVERSE_HOLO`) under `duplicateMode=create`, run the action, and assert the `createMany` payload's `data[0].language === "JP"` and `data[0].finish_type === "REVERSE_HOLO"`. The test is the regression that catches "we forgot to persist the enum field on the new row."

**Generalization**: applies to any CSV/JSON import that accepts enum-shaped fields. The enums must have an `OTHER` (or equivalent catch-all) value or the helper must be allowed to throw on unknown values — pick one and document the choice.

### 13. `mockReset` + `mockResolvedValue` (not `mockResolvedValueOnce` chains) when a test needs exactly one return

`vi.clearAllMocks()` clears call history but does NOT clear queued `mockResolvedValueOnce` returns. A later test in the same file inherits the prior test's queued returns FIFO, so the Nth call to a mocked function in the current test may receive what the (N+1)th call of the prior test was expected to receive. This is the "test passes in isolation but fails when the full file runs" bug class.

**Pattern**: in any test that needs exactly one return for a mocked function, use `mockReset` + `mockResolvedValue` at the top of the test, and add a comment explaining why:

```ts
// vi.clearAllMocks clears call history but not queued returns.
// mockReset wipes the queue, mockResolvedValue sets the single
// persistent return. The next test in this file is no longer
// affected by the prior test's mockResolvedValueOnce chain.
mock.mockReset();
mock.mockResolvedValue([expected]);
```

Only use `mockResolvedValueOnce` chains when the test intentionally exercises N distinct return values for N distinct calls, and add a comment at the bottom of the test explaining which calls consumed which queued returns. Without that comment, a future maintainer will not know which mocks are safe to refactor.

**Test pollution diagnosis recipe**: when a test fails only in the full-file run (passes in `-t "..."` isolation), the first thing to check is the previous test's queued `mockResolvedValueOnce` chain. Count the call count of the failing mock in the current test, then count how many of the previous test's queued returns would be consumed before the current test's first call. If those counts add up to the wrong return, that's the bug.

**Generalization**: applies to any Vitest test file with multiple `it`/`describe` blocks that share a mocked module. The CardForge `cf-e5-s3-multi-location-stock.test.ts` is the canonical example.

## Patterns from the bmad-dev-story correction (2026-06-02) — second round

The same-day **fresh** `bmad-code-review` (after the first-round correction landed) returned `BLOCKED` on a different shape of four points. The first round had fixed the "review forgot to update the code at one layer" bugs (sort column, language/finish persistence, atomic merge for existing identities); the second round surfaced bugs in **adjacent write paths** the first review had not exercised at all. The story-level lesson: an invariant partially enforced at one boundary (`CardItem.quantity` for an existing card on merge) is still not enforced at all the other boundaries (new card create, manual create, manual quantity edit, sale deduct, sale restore, page-level summary). The meta-pattern: after a bmad-dev-story correction resolves a review, run a "boundary walk" — list every place the invariant is touched and check each one.

### 14. CSV merge: coalesce same-batch new identities into a single card with multiple buckets

The first-round correction fixed the "merge an incoming row into an EXISTING card" path. The second-round review surfaced that **merge-mode new identities** (rows whose identity is not in the pre-import list) were being pushed straight to `pendingCreates` and creating one CardItem per row — so two same-batch Pikachu rows at different physical bins produced two CardItem rows, not one card with two buckets. The fix: a `pendingNewByIdentity: Map<identityKey, { data, buckets }>` accumulated during the row loop; second-and-later rows with the same identity (in merge mode) bump the data's `quantity` and the matching bucket's quantity (or append a new bucket entry at a new location). After the row loop, every entry in `pendingNewByIdentity` is materialized into `pendingCreates` in insertion order, then routed through the atomic `createManyWithInitialBucketsForOwner` helper.

**Pattern**: when a dedup identity is **new within the current import batch**, the action layer must coalesce the rows into a single pending entry exactly the same way it would coalesce against pre-existing data. The pre-existing identity map is the right starting point, but it is not the right *ending* point — the in-progress map is. The two maps are joined at the end of the row loop, not at the start.

```ts
// In the row loop, in merge mode, when the identity is new:
if (duplicateMode === "merge") {
  const existing = pendingNewByIdentity.get(identityKey);
  const rowData = { name, setCode, ..., quantity: row.quantity, ... };
  if (existing) {
    existing.data.quantity = (existing.data.quantity ?? 0) + row.quantity;
    const found = existing.buckets.findIndex(b => b.location === location);
    if (found >= 0) existing.buckets[found].quantity += row.quantity;
    else existing.buckets.push({ location, quantity: row.quantity });
    result.merged++;
  } else {
    pendingNewByIdentity.set(identityKey, { data: rowData, buckets: [{ location, quantity: row.quantity }] });
    result.merged++;
  }
  continue;
}
// After the row loop, materialize into pendingCreates:
for (const pending of pendingNewByIdentity.values()) {
  pendingCreates.push({ data: pending.data, buckets: pending.buckets });
}
```

**Test**: import a CSV with two rows that share an identity (e.g. two Pikachu rows at Bin A and Bin B) under `duplicateMode=merge`, run the action, and assert exactly one `cardItem.create` call (or one batched create) and two `cardItemLocation.create` calls. The regression test catches "we forgot to coalesce new-batch identities and the page shows two Pikachu rows."

**Generalization**: applies to any CSV/JSON import where a chaos-sorted or natural-language source can produce multiple rows for the same logical entity in one batch. The map-based coalescing pattern works for any `Map<identityKey, accumulator>` shape, and the per-key bucket list is the right place to capture per-bin "where" data that does not belong on the parent.

### 15. Atomic create-with-initial-buckets: helper accepts `buckets: [...]` per item, returns created rows in input order

The first-round correction kept using `createManyForOwner` (which returns no new ids) plus a `cardItemLocationRepo.createForOwner` re-fetch loop to write a matching bucket per row. The second-round review surfaced that this shape is **non-atomic** and **ambiguous** for duplicate create-mode rows with the same identity but different locations: the re-fetch's signature-based matching (name + set + number + condition + language + finish) cannot distinguish two rows with the same identity, so the first re-fetch hit pairs the wrong row to the wrong bucket.

**Pattern**: a single repo helper `createManyWithInitialBucketsForOwner(ownerId, items)` that opens ONE `prisma.$transaction` and, for each input item, calls `tx.cardItem.create({ data })` (singular, so the new id is captured into a paired `{ id, index }` list) and then `tx.cardItemLocation.create({ data })` using the new id. The helper returns the created CardItem rows in input order, so the action layer can pair rows to buckets deterministically without re-fetching by signature.

```ts
createManyWithInitialBucketsForOwner: async (ownerId, items) => {
  // 1. Validate at the boundary: every bucket quantity is a non-negative int;
  //    for each item, sum(buckets) === data.quantity (pre-flight invariant).
  // 2. Lot ownership check (one query, owner-scoped).
  // 3. Inside a single $transaction:
  //    for (let i = 0; i < items.length; i++) {
  //      const card = await tx.cardItem.create({ data: items[i].data });
  //      created.push({ id: card.id, index: i });
  //    }
  //    for (const entry of created) {
  //      for (const b of items[entry.index].buckets) {
  //        await tx.cardItemLocation.create({ data: { ..., card_item_id: entry.id, ... } });
  //      }
  //    }
  // 4. Return rows in input order via the .push'd index list.
}
```

The `buckets: [...]` array (instead of a single `bucket: {...}`) is what makes the helper work for both single-bucket and multi-bucket creates per CardItem. The CSV merge-mode pending-new path produces a multi-bucket entry; the CSV create-mode path produces a single-bucket entry; both call the same helper.

**Tests** (all required):
- The single-transaction shape: `$transaction` is called exactly once for the whole batch.
- `cardItem.createMany` is NOT used (we need ids back, and `createMany` does not return them by default).
- The pre-flight invariant guard rejects when `sum(buckets) != data.quantity` and never opens a `$transaction`.
- The rollback shape: when a bucket create fails inside the `tx`, the entire batch rolls back (assert the error message and that the call shape is still one `$transaction`).
- The input-order pairing: two create-mode rows with the same identity but different locations are paired to the right buckets (assert `tx.cardItemLocation.create` was called with `card_item_id: <row-1-id>, location: "Bin X"` and `card_item_id: <row-2-id>, location: "Bin Y"`).

**Generalization**: applies to any "create parent + create N children that reference the new parent" batch write path. The pattern (input-order paired list inside a single `$transaction` with pre-flight invariant validation) extends to `createSaleWithLineItems`, `createLotWithItems`, `createExpenseWithTags`. Anywhere the parent's id needs to be paired to a child that references it, the `createMany + re-fetch` shape breaks for ambiguous inputs; the `tx.create + .push({id,index})` shape does not.

### 16. Invariant alignment across every write boundary: a "boundary walk" pattern

The first-round correction fixed three invariants at three boundaries (sort column, language/finish, atomic merge). The second-round review surfaced four more invariants at four more boundaries (same-batch coalescing, atomic create, manual+ sales alignment, filtered summary). The story-level lesson is broader than any single boundary: **after resolving a review, walk every other place the same invariant is touched and check each one.** A "boundary walk" for this story's bucket invariant looks like:

| Write path | Atomic? | Bucket sum == quantity? | Fixed in which round? |
|---|---|---|---|
| Migration backfill | Yes (1 migration) | Yes (1:1) | Implementation |
| `setLocationForOwner` (bulk action) | Yes (`$transaction`) | Yes (collapse to 1 bucket) | Implementation + cleanup |
| `applyMergeStockForOwner` (CSV merge existing, with buckets) | Yes (`$transaction` + guard) | Yes | First-round correction |
| `applyMergeStockForOwner` (CSV merge into no-bucket card) | Yes (`$transaction` + guard) | Was: drift / is: yes (null-location seed absorbs pre-existing stock) | **Third-round correction** |
| `createManyWithInitialBucketsForOwner` (CSV create) | Yes (`$transaction` + guard) | Yes | Second-round correction |
| `createWithInitialBucketForOwner` (manual create) | Yes (`$transaction`) | Yes | Second-round correction |
| `updateQuantityForOwner` (manual edit / sales adjust) | Yes (`$transaction`) | Yes (rebalance) | Second-round correction |
| `deductCardInventoryAndSnapshotCogs` (sales decrement, with buckets) | Was: no / is: yes (added `adjustBucketQuantitiesForOwner`) | Was: drift / is: yes | Second-round correction |
| `deductCardInventoryAndSnapshotCogs` (sales decrement, no buckets) | Was: no / is: yes (helper reads current CardItem.quantity) | Was: zero-quantity bucket / is: yes (null-location bucket of post-deduct size) | **Third-round correction** |
| `restoreCardInventory` (sales restore / cancel, with buckets) | Was: no / is: yes | Was: drift / is: yes | Second-round correction |
| `restoreCardInventory` (sales restore, no buckets) | Was: no / is: yes (helper reads current CardItem.quantity) | Was: zero-quantity bucket / is: yes (null-location bucket of post-restore size) | **Third-round correction** |
| Page-level filtered summary | Was: unfiltered / is: narrowed to `summaryItems` | n/a (counted) | Second-round correction |
| `bulkUpdateForOwner` (archive / lot assign) | n/a (no quantity change) | n/a | Pre-existing |

**Pattern**: when implementing or correcting a story that introduces a new invariant, build a write-path table before the first commit. For each write path that touches either side of the invariant, mark whether the invariant holds at that boundary. This surfaces the "we forgot to enforce at this path" bugs before the review does. The first round of this story would have been more efficient if the developer had walked every path that mutates `CardItem.quantity` or `CardItemLocation.quantity` before submitting the first round.

**Generalization**: any time a story adds a derived or cross-model invariant (totals, sums, count consistency, status transitions, role/permission checks), build the write-path table as part of the plan. The cost of one table is a fraction of a `BLOCKED` review round.

### 17. Sales service deduct / restore: keep bucket totals aligned inside the same `$transaction`

The first-round correction did not touch the sales service. The second-round review surfaced that `deductCardInventoryAndSnapshotCogs` and `restoreCardInventory` were both updating `CardItem.quantity` inside a `$transaction` but never touching the `CardItemLocation` rows. The fix: a new helper `adjustBucketQuantitiesForOwner(tx, ownerId, cardItemId, delta)` that runs inside the same `$transaction` and applies the signed adjustment to the largest-quantity bucket (ties broken by lowest id), with three special cases:

- **No buckets exist** (legacy card or just-created card with no locations): the **second round** created a single null-location bucket with `Math.max(0, delta)`, and the **third round** corrected that to read the card's current post-mutation `CardItem.quantity` and create a single null-location bucket of that exact size. See pattern #21 for the full third-round fix and the regression test that locks the invariant for both negative and positive deltas. The third-round helper body is:

  ```ts
  if (buckets.length === 0) {
    const currentCard = await tx.cardItem.findFirst({
      where: { id: cardItemId, owner_id: ownerId },
      select: { quantity: true },
    });
    const bucketQty = Math.max(0, currentCard?.quantity ?? 0);
    if (bucketQty > 0) {
      await tx.cardItemLocation.create({
        data: { owner_id: ownerId, card_item_id: cardItemId, location: null, quantity: bucketQty },
      });
    }
    return;
  }
  ```
- **Adjustment empties a bucket** (e.g. a 3-unit bucket hits 0 after deducting 5 units that were partially restored from elsewhere): delete the bucket and carry the negative remainder into the next bucket.
- **Restored positive remainder exceeds the existing bucket set** (rare — happens when a sale is restored after the buckets were simplified by a later action): create a new null-location bucket to absorb the positive remainder.

```ts
async function adjustBucketQuantitiesForOwner(tx, ownerId, cardItemId, delta) {
  if (delta === 0) return;
  const buckets = await tx.cardItemLocation.findMany({
    where: { owner_id: ownerId, card_item_id: cardItemId },
    orderBy: [{ quantity: "desc" }, { id: "asc" }],
  });
  if (buckets.length === 0) {
    // Third-round correction: read current CardItem.quantity instead of
    // using Math.max(0, delta). See pattern #21 for the full rationale
    // and regression coverage.
    const currentCard = await tx.cardItem.findFirst({
      where: { id: cardItemId, owner_id: ownerId },
      select: { quantity: true },
    });
    const bucketQty = Math.max(0, currentCard?.quantity ?? 0);
    if (bucketQty > 0) {
      await tx.cardItemLocation.create({
        data: { owner_id: ownerId, card_item_id: cardItemId, location: null, quantity: bucketQty },
      });
    }
    return;
  }
  let remaining = delta;
  for (const bucket of buckets) {
    if (remaining === 0) break;
    const newQty = bucket.quantity + remaining;
    if (newQty > 0) {
      await tx.cardItemLocation.update({ where: { id: bucket.id }, data: { quantity: newQty } });
      remaining = 0;
    } else {
      await tx.cardItemLocation.delete({ where: { id: bucket.id } });
      remaining = newQty; // negative or zero
    }
  }
  if (remaining > 0) {
    await tx.cardItemLocation.create({
      data: { owner_id: ownerId, card_item_id: cardItemId, location: null, quantity: remaining },
    });
  }
}
```

**Tests** (the in-memory store in `sales-service.test.ts` is the canonical harness):
- A COMPLETED sale on a card with two buckets (`Bin A: 3, Bin B: 2`) decrements `CardItem.quantity` by the sale qty AND decrements the largest bucket (`Bin A`) by the same qty, leaving `Bin B` untouched. Assert `CardItem.quantity == 5 - qty` AND `sum(buckets) == CardItem.quantity`.
- A COMPLETED → PENDING transition restores the qty to the largest bucket, not the smallest. The bucket set is the deterministic inverse of the deduct path.
- A COMPLETED sale on a card with no buckets creates a single null-location bucket of size `post-deduct CardItem.quantity` (NOT `Math.max(0, delta)` — see the third-round correction and the regression test in pattern #21). The bucket store mock must track `Map<cardItemId, Map<bucketId, { location, quantity }>>` so the helper can be exercised through the in-memory path; `findMany` reads from it, `create` allocates a new id and inserts, `update` and `delete` mutate in place.

**Generalization**: any time a service-layer function mutates a "canonical" row inside a `$transaction` (CardItem.quantity, Sale.quantity, Lot.total_cost, etc.), audit every other model that derives from that canonical row and decide whether the derived value should also be mutated inside the same transaction. If yes, the helper belongs in the repo (not the service) so it can be called from `$transaction` callbacks. The third round's lesson: the helper's no-buckets branch cannot rely on the delta alone — it must look up the canonical row's current quantity, because the canonical row has already been mutated by the caller's `updateMany` before the helper runs, and the delta is signed (negative for deduct, positive for restore) rather than the post-mutation absolute value.

### 18. Filtered server-component summary: narrow bucket set to the filtered card set, not the owner

The first-round correction narrowed the page's `summaryItems` and the `locationOptions` dropdown, but the "Locations" summary tile in the filtered row was using the same `filteredBuckets` that the rest of the page used — which turned out to be the **full owner bucket list** because the page called `cardItemLocationRepo.listForOwner(ownerId)` twice with the same args. The second-round review surfaced that the filtered tile therefore counted locations from cards outside the filtered result set.

**Pattern**: in any server component that builds both an "all" summary and a "filtered" summary, the filtered summary must narrow its inputs to the filtered card set, even when the underlying repo helper does not take a `cardItemId` filter. The narrowing is a page-level concern because the page knows the filtered card ids; a repo helper would have to take both arguments and call them in a specific order.

```ts
const summaryItemIds = new Set(summaryItems.map((item) => item.id));
const narrowedFilteredBuckets = filteredBuckets.filter((bucket) =>
  summaryItemIds.has(bucket.card_item_id)
);
const filteredSummary = buildInventorySummary(summaryItems, narrowedFilteredBuckets);
```

**Test gap**: there is no automated test for this fix. The page is a Next.js server component and the existing test harness does not exercise the rendered output of a server component without a deep render-graph mock. The fix is four lines of plain `filter`, so a code review is the right level for this gate. Future stories that touch server-component summaries should add a focused unit test on the equivalent helper function (e.g. extract `buildInventorySummary` and the narrowing logic into a pure function, then test that pure function directly).

**Generalization**: any time a "filtered" metric shares its repo call with the "all" metric, verify the narrowed inputs are actually narrowed. This is a recurring bug class in server-component dashboards (the unfiltered helper is convenient, the filtered narrowing is a separate concern, and they often drift apart as the page evolves). The mitigation pattern is: extract the filter+aggregate into a pure function, test that pure function, and inline the narrowing in the page so a future change cannot accidentally bypass it.

### 19. Mock surface for a new repo helper: extend every existing test's `vi.mock("@/lib/db/owner-scope")` block

When the first-round correction added `applyMergeStockForOwner`, the test mocks had to be extended with a new method. When the second-round correction added three more helpers (`createManyWithInitialBucketsForOwner`, `createWithInitialBucketForOwner`, `updateQuantityForOwner`) plus an in-memory bucket store for the sales service test, every existing test that mocked `@/lib/db/owner-scope` or `@/lib/db/prisma` had to be updated. The pattern is mechanical but easy to miss in a `BLOCKED` review cycle:

1. **Action-level tests** (e.g. `inventory-actions-money.test.ts`, `cf-e2-s2-stabilization.test.ts`, `cf-e5-s2-bulk-lot-assignment-actions.test.ts`): add the new method name to the `vi.mock("@/lib/db/owner-scope")` factory object as `newMethod: vi.fn()`. The action will call it; the test asserts on it.
2. **Helper-level tests** (e.g. `cf-e5-s3-multi-location-stock.test.ts`): the `vi.mock("@/lib/db/prisma")` factory is the source of truth; the new helper's `$transaction` body must be tested by mocking `$transaction.mockImplementation((fn) => fn(txMock))` and asserting on the `txMock` methods.
3. **Sales service tests** (e.g. `sales-service.test.ts`): the `mockTx` helper must be extended to track a separate in-memory bucket store so the new `adjustBucketQuantitiesForOwner` can be exercised through the in-memory path. The bucket store is `Map<cardItemId, Map<bucketId, { location, quantity }>>`; `findMany` reads from it, `create` allocates a new id and inserts, `update` and `delete` mutate in place.
4. **Atomicity tests** (e.g. the `transaction atomicity` test in `sales-service.test.ts`): when a test hand-rolls a `tx` object (bypassing `mockTx`), it must include every method the new helper calls. Forgetting one (e.g. `cardItemLocation`) makes the test fail with `Cannot read properties of undefined` and the symptom looks like a production bug. Defend against this by including the full surface in the hand-rolled `tx`.

**Generalization**: when adding a new repo helper that uses a new model (e.g. `cardItemLocation.create`), audit every existing test file that mocks prisma or the owner-scope and add the new method to every mock surface in the same commit. Skipping this audit produces a wave of "Cannot read properties of undefined" failures in the next `pnpm test` run, which is confusing because the symptom looks like a production bug when it is actually a test-fixture gap.

### 20. Page-level narrowing belongs in the page, not in a helper, when the narrowing depends on local page state

The filtered Locations summary fix was four lines of `filter` inline in `InventoryPage`. The temptation to extract it to a "narrowBucketsToCards" helper was real, but rejected: the narrowing depends on `summaryItems` (a local page variable), and a helper would have to take both `filteredBuckets` and `summaryItemIds` as arguments. Inlining keeps the data flow obvious at the call site.

**Pattern**: extract a helper when the input is data; inline when the input is local page state. A test on an inlined filter is awkward (you'd have to render the page), so the test is a code review on the page itself, plus a future test on a pure-function equivalent if/when the logic is extracted.

**Generalization**: server components often have this "I know the filter set, but the helper would have to take it as an argument" shape. The default should be: inline for one-off narrowing, extract when the same narrowing appears in 2+ pages or when the narrowing is the core logic of a route. The cost of premature extraction is a helper signature that takes a half-dozen parameters and a test surface that has to mock all of them.

## Meta-pattern: how to run a second-round bmad-dev-story correction efficiently

The second-round correction inherited a story that had just been "corrected" 24 hours earlier. The fresh review found four new blockers. The correction cycle took ~45 minutes because the dev agent:

1. **Re-read the story artifact's review findings** (the BLOCKED section) before starting — the new blockers were enumerated there verbatim, with the trigger sentence ("independent focused review subagents" + the previous correction commit hash).
2. **Used `state.json`'s `last_artifacts` and `blockers` lists** as the authoritative scope, not memory or CONTINUE-HERE.md prose — those were stale by hours.
3. **Used the existing `cf-e5-s3-multi-location-stock-2026-06-02.md` reference file** (the first-round corrections) as the pattern library for the second round. The new patterns (#14–#20) extend, not duplicate, the first-round patterns (#1–#13). The reference file grew by ~300 lines; it did not split into a new file because the patterns all belong to the same story and the first-round reference is the natural continuation anchor.
4. **Re-ran the full validation bundle, not just the focused tests** — the second-round correction touched mocks in 4 test files (inventory-actions-money, rls-owner-scope, csv-import-large-batch, sales-service), and the focused tests alone would not have caught the cross-file test-mock drift. The full 370-test run is what surfaced the "the new helper is not on the action's mock" type of regressions.

The lesson for the next agent: a `bmad-dev-story` correction is not a one-shot. If a fresh review returns BLOCKED again, treat it as a new round with its own blockers, its own validation, and its own Dev Agent Record section. The story artifact grows; the state advances; the reference file grows. Do not try to rewrite the first-round Dev Agent Record — append a new "round 2" section.

## Patterns from the bmad-dev-story correction (2026-06-02) — third round

The same-day **second fresh `bmad-code-review`** (after the second-round correction landed) returned `BLOCKED` on two no-bucket invariant edges the boundary-walk had explicitly listed but whose "no-bucket" shape was a corner of the input space rather than a common case. The second round had walked every path and marked "yes, bucket sum equals quantity" for each one — but the marking was for the **with-buckets** case. The no-bucket / no-rows / no-presence shape of every write path was a separate question, and two paths (`applyMergeStockForOwner` for an existing no-bucket card, `adjustBucketQuantitiesForOwner` for a no-bucket card) failed it. The third-round lesson: a boundary walk is necessary but not sufficient. After walking every path with the common "with related rows" assumption, **walk the same paths with the "without related rows" assumption** and check each one.

### 21. No-bucket / no-rows / no-presence: the second axis of every boundary walk

The second-round boundary walk (pattern #16) listed every write path and confirmed `sum(buckets) == CardItem.quantity` for each one **with buckets present**. The third round surfaced that two of those paths silently violated the invariant when buckets were **absent**:

1. `applyMergeStockForOwner` with `buckets: [{ location: 'Bin A', quantity: 2 }]` on a card whose pre-existing buckets list is `[]` (legacy / brand-new card) and whose pre-existing `CardItem.quantity` is `5`. The pre-flight guard correctly rejects the payload because `2 != 5 + 2 = 7`, but the action layer is the one constructing that payload, and the layer was building it without seeding the pre-existing stock.
2. `adjustBucketQuantitiesForOwner` on a no-bucket positive-quantity card with `delta = -1` (sale deduct). The pre-existing helper created a null-location bucket with `Math.max(0, -1) === 0`, leaving `sum(buckets) == 0` and `CardItem.quantity == 2`. The invariant `sum(buckets) == CardItem.quantity` was broken at the end of the `$transaction`.

Both bugs share the same shape: the action layer / helper knew the **delta** but not the **pre-existing state** of the related row, and the "absent" case is the one where the pre-existing state matters most (because the helper's job is to *create* the related row, not to mutate an existing one).

**Pattern (action layer — CSV merge)**: when the pending bucket list for an existing card is empty, seed it with a null-location bucket carrying the pre-existing `CardItem.quantity` before adding the incoming row's quantity. If the incoming row's location is non-null, the row's quantity is added to a SECOND bucket entry (the seed bucket never grows), so the operator's physical location is preserved and the null-location seed only carries the legacy stock. If the incoming row's location is also null, the row's quantity grows the seed (so the two collapse into a single null-location bucket of the merged size).

```ts
// In the CSV import merge branch, when bucketsByCardId.get(duplicate.id) is []:
let merged = pendingBucketMerges.get(duplicate.id);
if (!merged) {
  const existing = bucketsByCardId.get(duplicate.id) ?? [];
  if (existing.length > 0) {
    merged = existing.map((b) => ({ location: b.location, quantity: b.quantity }));
  } else {
    // No buckets for the existing card. Seed with a null-location bucket
    // carrying the pre-existing quantity. The incoming row will either
    // grow this seed (if its location is also null) or push a new bucket
    // entry (if the operator gave a physical location).
    merged = [{ location: null, quantity: duplicate.quantity }];
  }
}
const found = merged.findIndex((b) => b.location === location);
if (found >= 0) {
  merged[found].quantity += row.quantity;
} else {
  merged.push({ location, quantity: row.quantity });
}
pendingBucketMerges.set(duplicate.id, merged);
```

**Pattern (repo / tx helper — sales service)**: when a no-buckets branch needs to know "how big should the new bucket be?", look up the canonical row's current quantity inside the same `$transaction`. The caller's `updateMany` has already mutated the canonical row, so reading it after the mutation is safe and gives the post-mutation absolute value. A `bucketQty > 0` guard prevents a zero-quantity zombie bucket from being created when a full deduct leaves the card at 0.

```ts
if (buckets.length === 0) {
  const currentCard = await tx.cardItem.findFirst({
    where: { id: cardItemId, owner_id: ownerId },
    select: { quantity: true },
  });
  const bucketQty = Math.max(0, currentCard?.quantity ?? 0);
  if (bucketQty > 0) {
    await tx.cardItemLocation.create({
      data: { owner_id: ownerId, card_item_id: cardItemId, location: null, quantity: bucketQty },
    });
  }
  return;
}
```

The corrected helper is symmetric: it works for negative deltas (sale deduct) and positive deltas (sale restore / cancel), and the `bucketQty > 0` guard is the only difference between a "deduct a positive-quantity card to zero" path (no bucket created) and a "deduct a positive-quantity card to a positive remainder" path (one bucket of the remainder).

**Tests** (all required):

- CSV merge into a no-bucket positive-quantity card (e.g. `quantity=5`) with an incoming row at a non-null location and quantity `2` → `CardItem.update` is called with `quantity: 7` AND `cardItemLocation.createMany` is called with `[{ location: null, quantity: 5 }, { location: "Bin A", quantity: 2 }]`. The mock must include `prisma.cardItem.findFirst` (the applyMergeStockForOwner ownership check) returning a card row, otherwise the helper throws "CardItem not found or not owned" and the test fails for the wrong reason.
- CSV merge into a no-bucket positive-quantity card (e.g. `quantity=5`) with an incoming row at a null location and quantity `2` → `CardItem.update` is called with `quantity: 7` AND `cardItemLocation.createMany` is called with a single entry `[{ location: null, quantity: 7 }]`. The seed-and-grow path collapses the two into one bucket.
- Sales partial deduct from a no-bucket positive-quantity card (`quantity=3`, sell `1`) → `CardItem.quantity` becomes `2` AND exactly one null-location bucket with `quantity: 2` is created. The test harness must track a separate in-memory bucket store (`Map<cardItemId, Map<bucketId, { location, quantity }>>`) and the corrected helper's `tx.cardItem.findFirst` must read from the same store. Without the bucket store, the corrected helper appears to no-op and the test silently passes (which is the worst possible failure mode — see "Test pollution / silent no-op" pitfall below).

**Pitfall — `Math.max(0, delta)` is wrong for negative deltas**: the second-round helper used `Math.max(0, delta)` because the writer thought "the net adjustment, clamped to a non-negative quantity, is what the bucket should hold." That is correct for a **delta** (signed), but the bucket needs a **post-mutation absolute value** (unsigned). On a negative delta with a positive pre-mutation quantity, `Math.max(0, delta)` is `0` while the post-mutation quantity is `>0`. Always look up the post-mutation quantity when the bucket is being created from scratch.

**Pitfall — the boundary-walk can still miss a "no related rows" corner**: a boundary walk that lists every write path and confirms the invariant with related rows present is necessary but not sufficient. Every write path has TWO axes: the related-rows-present axis and the related-rows-absent axis. The second axis is a corner of the input space (most operators never have an empty bucket set, or never have a card with no sales, etc.), and corners are where boundary walks most often fail. The "walk every path" rule must become "walk every path × every related-rows state."

**Generalization**: any time a story adds a derived / cross-model invariant, build a two-axis write-path table: rows = write paths, columns = invariant hold with related rows present, invariant hold with related rows absent. The second column is the one that gets neglected, and the bugs that land there are the ones that survive a single correction round and a single fresh review. Examples: `createSale` on a card with no `cardItem` link (already covered, but a re-verify is cheap), `assignLotForOwner` on a card with no `lotId` history (low risk, but the path exists), `exportRun` on an owner with no completed sales (the export's empty-state path).

## Meta-pattern: how to run a third-round bmad-dev-story correction efficiently

The third-round correction inherited a story that had been "corrected" twice in 24 hours. The fresh review found two new blockers. The correction cycle took ~30 minutes because the dev agent:

1. **Re-read the story artifact's review findings** (the second BLOCKED section) before starting — the new blockers were enumerated verbatim and reproduced a sentence each: "CSV merge into an existing positive-quantity no-bucket card still violates the bucket-total invariant" and "sales deduction on a no-bucket card can leave `CardItem.quantity` and `CardItemLocation` totals misaligned." Both blockers were also already listed in `state.json`'s `blockers` array, so the agent did not need to re-derive scope from prose.
2. **Used the boundary-walk table from pattern #16** as the starting point. The two new blockers mapped to two existing rows in the table (`applyMergeStockForOwner` existing merge, `deductCardInventoryAndSnapshotCogs` sales decrement). The third-round fix did not add a new write path — it patched two existing rows in the "no buckets present" column of the table.
3. **Localized each fix to the action layer or to the in-tx helper, with no new repo entry points.** The action layer was the right place to fix the CSV merge (because the seed is action-layer state, not repo state). The in-tx helper was the right place to fix the sales service (because the helper is the invariant boundary for bucket writes, and the caller's `updateMany` has already mutated `CardItem.quantity` by the time the helper runs, so the helper can read the post-mutation quantity inside the same `$transaction`). No new repo entry point was added; no new schema migration was needed; no new test fixture class was needed.
4. **Reused the existing in-memory bucket store harness** from the second-round sales deduct/restore tests (`Map<cardItemId, Map<bucketId, { location, quantity }>>`). The new sales-no-bucket test extended the same store with a `create` mock that allocates new ids and inserts in place. The new CSV-merge-no-bucket tests used the same `prisma.cardItem.findFirst` / `findMany` / `deleteMany` / `createMany` mock shape from the existing chaos-sort tests, with the one addition that `prisma.cardItem.findFirst` had to be wired to return the ownership-check card row inside `$transaction.mockImplementation((fn) => fn(prisma))`. Forgetting that one mock is the "test silently fails with the wrong reason" failure mode.
5. **Treated the test failures as a mock-shape problem, not a logic problem.** The first attempt at the new CSV-merge tests failed with "CardItem not found or not owned" — the same error a real production call would produce if the card was deleted between the import row's read and the helper's ownership check. The agent recognized this as a test-mock gap (the in-tx `prisma.cardItem.findFirst` was returning `undefined` because the outer `findFirst` was the only one mocked), added the missing mock, and the tests passed. The lesson: when a new test fails with the same error a production call would produce, check the mock surface before assuming a production bug.
6. **Updated the boundary-walk table in pattern #16 with two new rows** instead of leaving it stale. The table is the most reused artifact from the first reference file; leaving it stale would have made the next agent re-derive the same two missing boundaries on the next story with a similar invariant.

The lesson for the next agent: a third-round (or Nth-round) `bmad-dev-story` correction is still a real correction with its own blockers, its own validation, and its own Dev Agent Record section. Append a new "round N" section to the story artifact; append a new pattern to the reference file; update the boundary-walk table to include the new rows; treat the test failures as mock-shape problems before assuming production bugs. Do not try to rewrite any prior round's Dev Agent Record or pattern — append, do not replace. The reference file grew by ~150 lines; it did not split into a new file because all the patterns still belong to the same story and the prior rounds are the natural continuation anchor.

## Patterns from the bmad-dev-story correction (2026-06-02) — fourth round

The same-day **third fresh `bmad-code-review`** (after the third-round correction landed) returned `BLOCKED` on two new blockers that the boundary-walk table had listed but whose specific corner-case shape was still reachable in production. The fourth round took ~25 minutes because the dev agent applied the same meta-pattern as round three: re-read the review findings, localize the fix, add focused regression tests, rerun the full validation bundle, and append a new Dev Agent Record section.

### 22. Same-owner validation must cover EVERY create-path helper, not just the obvious ones

The third-round boundary walk (pattern #16) listed `createWithInitialBucketForOwner` as "Bucket sum == quantity: Yes" and marked it green. The fresh review surfaced that the helper did NOT verify `data.lotId` belongs to the current owner before creating the `CardItem` + initial bucket. The `createForOwner` helper (used by older code paths) already had this guard, and `createManyWithInitialBucketsForOwner` (used by CSV create) already had a batch lot-ownership check. But `createWithInitialBucketForOwner` (used by manual create via `createCardItemAction`) was missing the guard entirely.

**Pattern**: when a repo has multiple create helpers for the same model, the ownership/validation guard must be present in EVERY helper, not just the ones that were audited during the first implementation pass. A boundary walk that marks "yes, owner-scoped" for a write path is incomplete unless it explicitly confirms the guard is present in the source code, not just assumed from the helper's name or from adjacent helpers.

**Fix**: add the same pre-transaction `prisma.lot.findFirst({ where: { id: lotId, owner_id: oid } })` check to `createWithInitialBucketForOwner`, throwing `"Lot not found or not owned"` before opening `$transaction`. This mirrors the existing guards in `createForOwner` and `createManyWithInitialBucketsForOwner`.

**Test**: assert that calling `createWithInitialBucketForOwner` with a `lotId` that returns `null` from `prisma.lot.findFirst` throws before `$transaction` is opened, and assert that a valid `lotId` proceeds to create both the `CardItem` and the initial bucket.

**Generalization**: any time a model has N create/update helpers, a fresh code review should verify that every helper enforces the same ownership/validation rules. Do not assume that "helper A has the guard, so helper B (which does a similar thing) must also have it." Read the source.

### 23. Proportional scaling of child rows must defend against a zero denominator

The third-round boundary walk listed `updateQuantityForOwner` as "Bucket sum == quantity: Yes (rebalance)" and marked it green for the with-buckets case. The fresh review surfaced that the proportional scaling branch:

```ts
const share = Math.floor((b.quantity / oldTotal) * newQuantity);
```

produces `NaN` when `oldTotal === 0` (all existing buckets have quantity 0). This is reachable: a zero-quantity card exists, the operator applies a location (creating a zero-quantity bucket), then edits quantity upward. The `oldTotal === 0` case falls through to the proportional branch because `buckets.length > 0`, but the division by zero produces `NaN` before the Prisma update.

**Pattern**: before any proportional scaling or ratio-based distribution, explicitly guard against a zero denominator. When the denominator is zero, the proportional approach is undefined; fall back to a deterministic non-proportional behavior that preserves the invariant. For bucket rebalance, the fallback is: delete all zero-quantity buckets and create a single bucket at the largest bucket's location (or null if no buckets) with `quantity: newQuantity`.

```ts
if (oldTotal === 0) {
  if (buckets.length > 0) {
    await tx.cardItemLocation.deleteMany({
      where: { owner_id: oid, card_item_id: cardItemId },
    });
    await tx.cardItemLocation.create({
      data: {
        owner_id: oid,
        card_item_id: cardItemId,
        location: buckets[0].location,
        quantity: newQuantity,
      },
    });
  } else {
    await tx.cardItemLocation.create({
      data: {
        owner_id: oid,
        card_item_id: cardItemId,
        location: null,
        quantity: newQuantity,
      },
    });
  }
  return { id: cardItemId, quantity: newQuantity };
}
```

**Test**: create a card with two buckets both at quantity 0, then call `updateQuantityForOwner` with `newQuantity = 5`. Assert that `deleteMany` is called, `create` is called with `quantity: 5`, and no `update` calls are made (the proportional branch is never reached).

**Generalization**: any time a write path computes a ratio or proportion from an aggregate of existing child rows, add an explicit `if (denominator === 0)` guard before the division. The fallback behavior depends on the domain: for bucket rebalance, collapse to a single bucket; for cost allocation, skip or throw; for percentage calculations, return 0 or 100. The important thing is that the zero-denominator case is handled deterministically, not left to `NaN`.

### 24. Round-4 meta-pattern: the correction surface shrinks, but the review depth stays the same

The fourth round fixed only two blockers (vs. four in round two and three in round one), but the validation and artifact update discipline was identical: read the review findings, localize the fix, add focused regression tests, run the full validation bundle (not just focused tests), update all BMad artifacts, commit, and append a new Dev Agent Record section. The time per blocker decreased because the agent had already internalized the repo's mock patterns, the test harness shapes, and the artifact update sequence.

**Pattern**: as a story progresses through correction rounds, the time per blocker should decrease, but the rigor should not. The same validation gates, the same artifact updates, and the same evidence reporting apply to a one-line fix as to a twenty-line fix. Skipping gates because "this is just a small correction" is how regressions slip in.

**Generalization**: this applies to any multi-round correction workflow. The Nth round is not "almost done, so we can relax"; it is "the review found a new gap, so we apply the same discipline to close it." The story artifact grows with each round; the reference file grows; the boundary-walk table grows. These are assets for the next story, not overhead to minimize.
