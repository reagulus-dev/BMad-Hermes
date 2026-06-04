# CardForge multi-location stock no-bucket invariant review pitfall

Use this reference when reviewing CardForge/Prisma inventory stories where `CardItem.quantity` is canonical and `CardItemLocation` buckets must satisfy `sum(buckets.quantity) == CardItem.quantity`.

## Key lesson

Post-correction reviews must include **no-bucket positive-quantity cards**, not only the normal migrated/backfilled path where every card already has buckets.

A correction can pass tests for:
- same-batch CSV coalescing,
- atomic create-with-buckets,
- manual create/update bucket reconciliation,
- sales deduct/restore with existing buckets,

while still failing when an existing `CardItem` has `quantity > 0` and no `CardItemLocation` rows.

## Blocker patterns

### 1. CSV merge into existing no-bucket card

Check merge mode for an existing duplicate identity:

- Target quantity is usually `duplicate.quantity + row.quantity`.
- Pending buckets may be seeded from `bucketsByCardId.get(duplicate.id) ?? []`.
- If the card has no buckets, the bucket list contains only incoming row quantities.
- A repo invariant guard then either rejects `sum(buckets) != target quantity`, or worse, writes a mismatched bucket set.

Block unless the code preserves the pre-existing no-bucket stock, e.g. by creating a null-location bucket for the pre-existing quantity before applying incoming row buckets, or by routing through a helper that can reconcile from the current card quantity.

Required focused regression:
- existing owned card with `quantity > 0`
- no buckets returned for that card
- CSV duplicate-mode `merge`
- incoming row quantity at a physical location
- expected bucket total equals the new `CardItem.quantity` and includes pre-existing stock in a deterministic bucket (often null-location)

### 2. Sales partial deduct from no-bucket card

Check the sales service path when a consuming sale decrements inventory and then adjusts buckets.

A common bug:
- `CardItem.quantity` is decremented first.
- bucket helper receives a negative delta.
- no-bucket branch creates `quantity: Math.max(0, delta)`, which is zero for negative deltas.
- after a partial sale from quantity 3 to 2, bucket sum is still 0, not 2.

Block unless no-bucket partial deduct leaves buckets aligned with the post-sale quantity, typically a null-location bucket equal to remaining quantity. Restore/update/delete transitions must remain aligned too.

Required focused regression:
- positive-quantity no-bucket card
- completed sale quantity less than current quantity
- post-sale `CardItem.quantity` equals expected remainder
- bucket sum equals that same remainder
- restore/status transition keeps bucket sum aligned

## Review stance

- No-bucket positive-quantity rows are realistic after legacy cleanup, partial migrations, failed prior writes, or intentionally allowed repository helpers.
- Passing tests with existing bucket fixtures do not prove this edge case.
- If the story claims the invariant holds at every production write path, no-bucket edge cases are blockers, not notes.
