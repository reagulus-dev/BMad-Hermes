# CardForge CF-E2-S3: ViMock Type Widening Fix (2026-05-29)

## Problem

`corepack pnpm typecheck` failed with TS2339 errors in `tests/unit/rls/rls-owner-scope.test.ts`:

```
tests/unit/rls/rls-owner-scope.test.ts(136,30): error TS2339:
  Property 'mockImplementation' does not exist on type '(ownerId: number) => Promise<...>'
```

The same pattern appeared on lines 91, 104, 123, 155, 168, 190.

## Root Cause

`vi.mock` factories return the actual TypeScript type of the exported value. When `owner-scope.ts` exports typed function signatures (e.g., `listByOwner: (ownerId: number) => Promise<Sale[]>`), the mock created inside the factory has that exact callable signature — not a `vi.fn()` instance. Therefore `.mockImplementation()` and `.mockResolvedValue()` don't exist on the type.

The tests passed at runtime because Vitest's runtime mock objects ARE callable and do support these methods, but TypeScript's type system won't allow the method calls on the typed mock.

## Fix

Cast the mock method to `ReturnType<typeof vi.fn>` before calling the mock method:

```typescript
// Before (TS2339):
saleRepo.listByOwner.mockImplementation((requestedOwnerId: number) => { ... });

// After (type-safe):
(saleRepo.listByOwner as ReturnType<typeof vi.fn>).mockImplementation((requestedOwnerId: number) => { ... });
```

## Affected Files

- `tests/unit/rls/rls-owner-scope.test.ts` — all repo method mocks
- `tests/unit/cf-e2-s2-stabilization.test.ts` — pre-existing mock return shapes missing required fields (cogs_pence, status, timestamps, fees)

## The Pre-Existing Mock Shape Problem (cf-e2-s2-stabilization.test.ts)

The stabilization test also had incomplete mock return objects that passed at runtime via `as any` casts but failed typecheck after those casts were removed. The fix required adding all required Prisma fields:

```typescript
// Sale mock must include:
{
  id, owner_id, platform, sale_date, sale_price_pence, quantity,
  status, cardItemId, notes,
  created_at, updated_at,
  platform_fee_pence, payment_fee_pence,
  shipping_charged_pence, shipping_cost_pence,
  cogs_pence
}

// CardItem mock must include:
{
  id, owner_id, name, quantity, archived, cost_basis_pence,
  created_at, updated_at, notes,
  set_name, set_code, card_number, condition, lotId,
  status
}
```

## Pattern for Future ViMock Mocks in CardForge

When mocking repo methods from `owner-scope.ts` or similar typed modules:

```typescript
// Inside vi.mock factory:
vi.mock("@/lib/db/owner-scope", () => {
  const mockSaleRepo = {
    listByOwner: vi.fn(),
    createForOwner: vi.fn(),
    updateForOwner: vi.fn(),
  };
  return { saleRepo: mockSaleRepo };
});

// When using in tests, cast if TypeScript complains:
(saleRepo.listByOwner as ReturnType<typeof vi.fn>).mockResolvedValue([...]);
```

## Related

- `references/react-vitest-vi-mock-hoisting-fix.md` — related Vitest mock hoisting pitfalls