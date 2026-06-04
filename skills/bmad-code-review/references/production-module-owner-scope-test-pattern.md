# Production-module owner-scope test pattern (Vitest + TypeScript)

Concrete pattern for testing owner-scoped Prisma repository helpers in `src/lib/db/owner-scope.ts` using Vitest with `vi.mock`.

## Key technique: dynamic import inside test for mock access

Because Vitest hoists `vi.mock` calls, the mocked module is not yet available via a static import at the top of the test file. To access the mock's spy functions (for `.mockResolvedValue`, `.toHaveBeenCalledWith`, etc.), import the mock dynamically *inside* each test:

```typescript
import { cardItemRepo, saleRepo } from "@/lib/db/owner-scope";

// vi.mock is hoisted — module is registered before tests run
vi.mock("@/lib/db/prisma", () => {
  const mockPrisma = {
    lot: { findFirst: vi.fn(), ... },
    cardItem: { findFirst: vi.fn(), create: vi.fn(), update: vi.fn(), ... },
    sale: { findFirst: vi.fn(), create: vi.fn(), update: vi.fn(), ... },
    // ...remaining models
  };
  return { prisma: mockPrisma };
});

describe("cardItemRepo (production module)", () => {
  beforeEach(() => { vi.clearAllMocks(); });

  it("should reject when lotId belongs to a different owner", async () => {
    // Dynamic import — gets the hoisted mock instance
    const { prisma } = await import("@/lib/db/prisma");
    (prisma.lot.findFirst as ReturnType<typeof vi.fn>).mockResolvedValue(null);

    await expect(
      cardItemRepo.createForOwner(1, { name: "Pikachu", condition: CardCondition.NM, costBasisPence: 100, lotId: 99 })
    ).rejects.toThrow("Lot not found or not owned");
  });
});
```

## Why dynamic import

`vi.mock` creates module-level mocks that are registered before any tests run. The module namespace is live, but the import reference captured at the top of the test file (e.g., `import { prisma }`) resolves *before* the mock is active in hoisted files. Dynamic `await import(...)` inside the test body gets the current live mock.

## Minimal prisma mock shape

The mock must include ALL models referenced in `src/lib/db/owner-scope.ts` (even if not all are called in a given test) to avoid runtime errors from the production module trying to access missing properties:

```typescript
const mockPrisma = {
  lot: { findFirst: vi.fn(), findMany: vi.fn(), create: vi.fn(), update: vi.fn(), delete: vi.fn() },
  cardItem: { findFirst: vi.fn(), findMany: vi.fn(), create: vi.fn(), update: vi.fn(), delete: vi.fn() },
  sale: { findFirst: vi.fn(), findMany: vi.fn(), create: vi.fn(), update: vi.fn(), delete: vi.fn() },
  expense: { findFirst: vi.fn(), findMany: vi.fn(), create: vi.fn(), update: vi.fn(), delete: vi.fn() },
  exportRun: { findMany: vi.fn(), create: vi.fn() },
  userProfile: { findUnique: vi.fn() },
};
```

## Test structure: one describe per repo, describe blocks per method

```typescript
describe("cardItemRepo (production module)", () => {
  describe("createForOwner: lotId same-owner check", () => {
    it("should succeed when lotId belongs to the same owner", ...);
    it("should reject when lotId belongs to a different owner", ...);
    it("should reject when lotId does not exist", ...);
    it("should succeed when no lotId is provided", ...);
  });
  describe("updateForOwner: lotId same-owner check", () => {
    it("should succeed when updating lotId to a same-owner lot", ...);
    it("should reject when new lotId belongs to another owner", ...);
    it("should succeed when setting lotId to null", ...);
  });
});

describe("saleRepo (production module)", () => {
  describe("createForOwner: cardItemId same-owner check", () => {
    // similar 4 cases
  });
  describe("updateForOwner: cardItemId same-owner check", () => {
    // similar 3 cases (set to null is allowed without lot lookup)
  });
});
```

## Key pitfall: test-only injectable duplication

If tests import from `tests/unit/owner-scope.test-injectable.ts` (a duplicate reimplementation), they can pass even if the *production* same-owner checks are removed from `src/lib/db/owner-scope.ts`. The injectable is a separate code path — it is not evidence for the production module.

Signals of this pitfall:
- `import { createLotRepo, createCardItemRepo, createSaleRepo } from "./owner-scope.test-injectable"`
- Tests use a factory function to create a repo rather than calling the exported singleton from `src/lib/db/owner-scope.ts`
- `server-only` is aliased in vitest config but tests still only use the injectable

The fix: mock `@/lib/db/prisma` and import the production module directly.

## `server-only` in Vitest

In `vitest.config.ts`:
```typescript
resolve: {
  alias: {
    "server-only": path.resolve(__dirname, "./tests/server-only.js"),
  },
},
```

The mock file can be minimal:
```javascript
// tests/server-only.js
export default {};
```

This allows `import "server-only"` in production source to resolve without error in test context.