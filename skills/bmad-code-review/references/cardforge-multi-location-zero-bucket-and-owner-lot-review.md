# CardForge multi-location stock: zero-bucket and owner-lot review pitfalls

Use this reference when reviewing CardForge/Prisma inventory stories where `CardItem.quantity` remains canonical and `CardItemLocation` buckets are the per-location breakdown.

## Key lesson

After prior bucket-invariant corrections, do not stop at the named no-bucket cases. Re-audit **owner-scoped related IDs** and **zero-total bucket sets** introduced by the new helper paths.

Passing tests for positive no-bucket cards, atomic create-with-buckets, and sales partial deduct can still miss two production-grade blockers:

1. A new helper that creates a `CardItem` plus buckets may bypass same-owner `lotId` checks.
2. A card can have existing bucket rows whose total is `0`; this is different from “no buckets” and can break proportional rebalance logic.

## Blocker pattern 1: create-with-initial-bucket helper missing same-owner `lotId` validation

When a new repo helper creates a `CardItem` and its initial `CardItemLocation` bucket in one transaction, compare it against older owner-scoped create helpers.

Block if:

- Manual create action passes a user-controlled `lotId` into the helper.
- The helper validates owner id and bucket quantities but does not verify the provided `lotId` belongs to the same owner.
- The Prisma relation is `CardItem.lotId -> Lot.id` only, without a composite owner-consistent FK like `(lot_id, owner_id) -> (id, owner_id)`.

Why it matters:

- The otherwise owner-scoped manual create path can attach a new card to another owner's lot by guessed ID.
- This violates owner-scope guarantees even if the card row and bucket row themselves use the current owner.

Required correction:

- Add the same preflight owned-lot check used by existing `createForOwner` / batch create helpers.
- Add focused regression coverage for wrong-owner `lotId` rejection on the new create-with-bucket helper and/or manual create action.

## Blocker pattern 2: zero-total existing buckets are not the same as no buckets

Do not only test `buckets.length === 0`. A valid production sequence can create one or more bucket rows with quantity `0`:

- A zero-quantity card exists.
- The operator applies a location, collapsing the card to a single bucket with `quantity: card.quantity` (0).
- The operator later edits the card quantity upward.

Block if quantity rebalance code:

- Computes `oldTotal = sum(buckets.quantity)`.
- Enters proportional scaling whenever `buckets.length > 0`.
- Divides by `oldTotal` without handling `oldTotal === 0`.

Impact:

- `0 / 0` yields `NaN` and can fail the Prisma update or produce invalid bucket quantities.
- The manual quantity update path is blocked instead of preserving `sum(CardItemLocation.quantity) == CardItem.quantity`.

Required correction:

- Either avoid creating zero-quantity buckets in location assignment helpers, or
- Treat `oldTotal === 0` like the no-bucket case when increasing to a positive quantity: create one deterministic bucket (for example null-location or the existing target location) whose quantity equals the new `CardItem.quantity`.
- Add focused regression coverage for existing zero-total bucket set → positive quantity update.

## Review checklist additions

- Compare every new `CardItem` create helper against older owner-scoped helper patterns for related-row ownership (`lotId`, `cardItemId`, project/listing IDs, etc.).
- Check `buckets.length === 0` and `sum(buckets.quantity) === 0` as separate edge cases.
- Include zero-quantity card paths: import skip/create behavior, manual create, apply-location, manual quantity edit, sales deduct/restore, and archive/unarchive if present.
- Treat passing validation as insufficient if tests cover only positive buckets and no-bucket positive cards.
