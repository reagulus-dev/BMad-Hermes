# Next.js + Prisma CRUD Review Pattern — CardForge CF-E1-S3

Session-specific reference distilled from a CardForge BMad review around `CF-E1-S3`.

## Context

The story implemented owner-scoped Lots and Inventory CRUD in a Next.js app with Prisma repositories, Zod validation schemas, server actions, and dynamic pages:

- `src/lib/validation/schemas.ts`
  - `lotCreateSchema`, `lotUpdateSchema`, `cardItemCreateSchema`, `cardItemUpdateSchema`, `inventoryFilterSchema`
- `src/lib/db/owner-scope.ts`
  - lot detail summary/calculation helpers
  - archive operations
  - inventory filtering
  - card item CRUD/archive/delete
- `src/lib/actions/inventory.actions.ts`
  - server actions using `safeParse` and `revalidatePath`
- UI routes:
  - `/lots`
  - `/lots/[id]`
  - `/inventory`

## Review checklist for this class

When reviewing a similar Next.js + Prisma CRUD story:

1. **Route rendering boundary**
   - Confirm pages that touch owner-scoped DB data are not accidentally statically prerendered at build time.
   - Treat a passing `next build` with dynamic route output for those pages as relevant evidence.
   - If the app uses development owner seams, verify production-facing pages/actions do not silently map all users to one owner.

2. **Validation boundary**
   - Check create/update/filter Zod schemas directly.
   - Verify update schemas do not allow identity/ownership fields to be changed by client input.
   - Verify filters coerce/validate optional values without broadening access.

3. **Server action boundary**
   - Require `safeParse` or equivalent before repository calls.
   - Confirm error paths return structured/action-consumable failures rather than throwing generic errors for expected validation failures.
   - Confirm successful mutations revalidate the exact affected paths (`/lots`, `/lots/[id]`, `/inventory`) and do not leave stale list/detail views.

4. **Prisma owner scope and relation checks**
   - List/read/update/archive/delete helpers should constrain by owner at the query boundary.
   - Creates that attach to a related entity, such as creating a card item for a lot, must prove the related row belongs to the same owner before writing.
   - Filter combinations should be expressed in one owner-scoped Prisma query where practical, rather than filtering after fetching a broader set.

5. **Calculation correctness**
   - For summary fields such as `cardCount`, `allocatedCost`, `soldRevenue`, and `profit`, inspect formula semantics and tests.
   - Verify archived/deleted rows are included or excluded consistently with product intent.
   - Watch for null/undefined numeric fields and decimal/currency rounding assumptions.

6. **Evidence expectations**
   - Focused schema tests and calculation/repository tests are valuable, but the review should still inspect the implementation paths.
   - A broad unit-suite pass is not enough if the new tests do not cover filter combinations, owner boundaries, or summary math.
   - Lint warnings should be classified carefully: a newly introduced warning in the reviewed slice can fail the evidence gate if the project treats warnings as gating; clearly distinguish pre-existing unrelated warnings.

## Verdict guidance

Use `PASS WITH NOTES` when implementation and tests are sound but auth/runtime owner resolution remains a future seam or live DB smoke was not run.

Use `BLOCKED` when:

- production-facing actions/pages use a hardcoded/dev owner without explicit dev-only gating,
- create/update operations can attach to another owner’s related row,
- filters fetch broader owner/tenant data and narrow it only in memory,
- claimed summary math is untested or demonstrably wrong,
- route build output contradicts the story claim that DB-backed pages avoid static prerendering.
