# Production-module owner-scope test review

Use when reviewing Prisma/ORM owner-scoped repository tests after a blocker asked for production-helper coverage.

## Key distinction

Behavioral tests are not automatically production-boundary tests. A suite can remove placeholders and regex/source checks, pass many behavioral cases, and still be invalid evidence if it imports a test-only clone of the repository logic.

Valid evidence:
- Mock/stub the production Prisma/client boundary.
- Import the production module under review, e.g. `src/lib/db/owner-scope.ts`.
- Call the real exported helpers such as `cardItemRepo.createForOwner`, `cardItemRepo.updateForOwner`, `saleRepo.createForOwner`, and `saleRepo.updateForOwner`.
- Assert cross-owner related rows reject before writes and same-owner related rows proceed to the expected create/update call.

Invalid evidence, even when tests are otherwise behavioral:
- `tests/.../owner-scope.test-injectable.ts` or similar factory functions that reimplement repository behavior for tests.
- A local duplicate `requireOwnerId`, `createCardItemRepo`, `createSaleRepo`, etc.
- Tests that only prove the duplicate implementation behaves correctly.
- Config changes such as a `server-only` alias or test `DATABASE_URL` when the test still does not import the production module.

## Review stance

If the prior blocker specifically required production-helper tests, keep the review BLOCKED when the correction still tests a duplicate injectable implementation. Give credit for removing placeholders/source-string checks, but do not pass the gate until the test seam is wrapped around the production module.

## Correction recipe

1. Mock the production DB module before importing the repository module, e.g. mock `src/lib/db/prisma` to return a Prisma-like object with spies.
2. Keep `server-only` test alias/mocking if needed so the production module can load in Vitest.
3. Import the real owner-scope module after mocks are registered.
4. Exercise the exported production repos directly.
5. Assert both negative and positive paths:
   - missing/invalid owner id rejects,
   - read/list queries include `owner_id`,
   - update/delete first prove ownership,
   - `CardItem.lotId` create/update rejects cross-owner lots and allows same-owner lots,
   - `Sale.cardItemId` create/update rejects cross-owner card items and allows same-owner card items.
