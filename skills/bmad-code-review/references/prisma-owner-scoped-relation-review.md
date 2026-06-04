# Prisma owner-scoped relation review pattern

Use when a BMad story implements Prisma models/repositories with `owner_id`, tenant IDs, household IDs, organization IDs, or similar row ownership.

## Review risk

Independent foreign keys do not prove same-owner integrity. A table can have both:

- `card_items.owner_id -> user_profiles.id`
- `card_items.lot_id -> lots.id`

...while still allowing `card_items.owner_id = A` and `card_items.lot_id` pointing to a `lots` row owned by `B`, unless the implementation enforces same-owner relation checks or the DB uses owner-aware composite constraints.

## What to inspect

For every repository/service create/update helper that accepts a related row ID:

- Identify relation ID inputs such as `lotId`, `cardItemId`, `projectId`, `teamId`, `householdId`, `routeId`, `workerId`, etc.
- Confirm the helper validates `ownerId`/tenant ID itself.
- Confirm it verifies each referenced related row belongs to the same owner/tenant before writing.
- Prefer a transaction when checking related-row ownership and then writing a dependent row.
- Check schema/migration hardening:
  - composite unique/index constraints on `(id, owner_id)` for parent rows, and
  - composite FKs from child `(related_id, owner_id)` to parent `(id, owner_id)`, where appropriate and supported by the migration style.
- If DB-level hardening is deferred, the story/review must explicitly say this is a service-layer-only stance and preserve DB hardening as carry-forward.

## Test evidence requirements

Do not accept placeholder tests such as `expect(true).toBe(true)` or local duplicate implementations of private helpers as evidence for owner scoping.

Require focused tests that exercise the production helper boundary, typically with a mocked Prisma module or other repository seam. Cover:

- invalid/missing owner ID is rejected by production helper paths
- read/list queries include the owner filter
- update/delete first prove current row ownership before writing/deleting
- create/update rejects cross-owner relation IDs
- allowed same-owner relation IDs still pass

### Post-correction evidence pitfall

After a BLOCKED review asks for production-helper owner-scope tests, do not accept a correction that only:

- adds test-only helper functions that duplicate the intended ownership checks,
- asserts source text with regex/string matching,
- keeps placeholder assertions such as `expect(true).toBe(true)`, or
- says tests cover production logic without importing/calling the production repository functions.

A valid correction should mock/stub the Prisma boundary and call the real helpers (for example `cardItemRepo.createForOwner`, `cardItemRepo.updateForOwner`, `saleRepo.createForOwner`, `saleRepo.updateForOwner`). Assert that missing/cross-owner related rows reject before writes, and same-owner rows proceed to the expected `create`/`update` call.

## Review verdict guidance

Use `BLOCKED` when the story acceptance criteria require owner-scoped writes and relation ID helpers can create cross-owner links, or when tests claim owner-scope coverage but do not exercise production helpers.

Use `PASS WITH NOTES` only when same-owner checks exist in the service/repository path, current story explicitly defers DB-level composite constraints, and focused tests cover the production boundary.
