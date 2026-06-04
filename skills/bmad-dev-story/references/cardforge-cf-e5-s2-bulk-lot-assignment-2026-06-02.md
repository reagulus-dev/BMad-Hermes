# CF-E5-S2 — Bulk Lot Assignment and Unassigned-Lot Filter (2026-06-02)

CardForge story that landed clean (332/332 tests, all validation gates pass, no Prisma schema change). The implementation surfaced three patterns that recur in any "bulk update with server-side calculation + nullable filter" story, plus a CardForge-specific cost-basis contract that must not be silently changed in future stories.

## Reusable patterns (any project)

### 1. Narrower repo helper when the client must NOT supply a calculated value

When a story requires a server-side authoritative calculation (e.g. cost-basis recalc, per-unit allocation, derived status) and explicitly forbids the client from submitting the computed field, **do not** extend an existing `bulkUpdateForOwner` boundary with a new optional `costBasisPence` field. Add a narrower repo helper such as `assignLotForOwner(ownerId, ids, lotId)` that:

- Verifies owner-scoped ownership of every selected row and of any referenced parent (target lot).
- Computes the derived value internally.
- Calls `updateMany` with the computed value.
- Returns `{ count }` so callers can refresh.

The narrower boundary encodes the "client cannot influence the calculation" rule at the type system level. The existing `bulkUpdateForOwner` is preserved for true client-supplied bulk patches (archive, location).

**Test pattern**: at least one test that sends a malicious `costBasisPence` in the form and asserts the repo is called with the server-computed value, not the client-supplied one.

### 2. Deliberate string sentinel for null filter values

For "filter to rows where column IS NULL" (or any nullable filter), **never** overload numeric 0, empty string, or any other "natural" empty value. Use a deliberate string sentinel such as `__none` exposed as a named constant.

Schema pattern (zod):

```ts
export const LOT_UNASSIGNED_SENTINEL = "__none";
export const inventoryLotFilterValueSchema = z.union([
  z.literal(LOT_UNASSIGNED_SENTINEL),
  z.coerce.number().int().positive(),  // rejects 0 and negatives
]);
```

Reject `0` explicitly in the schema. The point of the sentinel is to be unambiguous; overloading numeric 0 reintroduces the ambiguity.

Repo pattern: discriminated union on the filter value, mapped to a Prisma where clause:

```ts
const lotWhere =
  typeof filters.lotId === "number"
    ? { lotId: filters.lotId }
    : filters.lotId === LOT_UNASSIGNED_SENTINEL
    ? { lotId: null }
    : {};
```

**Test pattern**: at least one assertion that the sentinel maps to `lotId: null` in the where clause, plus one that `0` is rejected by the schema.

### 3. Page passes raw URL string to schema; do not pre-coerce with `Number()`

When the page parses Next.js `searchParams` and forwards to a Zod schema, **do not** pre-coerce with `Number()` if the schema needs to discriminate between a numeric value and a string sentinel. The coercion destroys the sentinel (`Number("__none")` is `NaN`).

```ts
// WRONG — kills the sentinel before the schema sees it
lotId: sp.lotId ? Number(sp.lotId) : undefined,

// RIGHT — pass the raw string, let z.union + z.literal match first
lotId: sp.lotId || undefined,
```

**Test pattern**: at least one URL parameter test that `?lotId=__none` survives to the repo as the sentinel literal.

## Two visible controls > one ambiguous control

When the user can do two semantically opposite things to the same field (assign vs clear), use two distinct server actions, not one overloaded action with a flag. Reasons:

- The UI can keep the two controls visibly separate (`Assign lot` vs `Clear lot` buttons, distinct disabled states, distinct copy).
- Validation rules diverge (assign requires a non-empty value, clear forbids any value).
- Cost / side-effect semantics differ (assign recomputes, clear zeros).
- Tests can assert each action's boundary independently.

Don't paper over the asymmetry with a single `assignCardItemsLotBulkAction({ lotId: "" })` shorthand. Split the boundary.

## CardForge-specific cost-basis contract (do not silently change)

`cardItemRepo.assignLotForOwner` writes the per-unit `cost_basis_pence` for every selected owned row using:

```text
selectedTotalQuantity > 0:
  costPerCardPence = Math.max(1, Math.round(lot.total_cost_pence / selectedTotalQuantity))
selectedTotalQuantity == 0:
  costPerCardPence = 0
```

- The `Math.max(1, ...)` floor guarantees a positive non-zero per-unit basis when there is at least one card.
- The explicit zero-quantity branch returns 0 to avoid NaN/Infinity on a degenerate selection.
- `cost_basis_pence` is millipence (×1000) since CF-E3, even though the column name still ends in `_pence`.

Carry-forward: future stories must not silently swap to `Math.ceil` (over-allocates) or any other rounding rule without a per-unit cost audit and a clear contract update. The formula is the documented cost-basis contract for bulk-lot assignment.

## Story metadata

- Story: `_bmad/artifacts/stories/CF-E5-S2-bulk-lot-assignment-and-unassigned-filter.md`
- Evidence: `_bmad/artifacts/evidence/CF-E5-S2/validation-summary.md`
- New tests: 34 (23 repo+schema + 11 actions)
- Suite before: 298 → after: 332
- Status: `implemented_not_reviewed`, awaiting `bmad-code-review`
