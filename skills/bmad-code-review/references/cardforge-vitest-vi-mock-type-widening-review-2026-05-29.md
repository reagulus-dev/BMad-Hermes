# CardForge: vi.mock Type Widening in Vitest Unit Tests — Reviewer Note

## How to Spot This in Code Review

When reviewing unit test files, watch for:

```typescript
// TS2339 in typecheck but tests pass at runtime:
saleRepo.listByOwner.mockImplementation(...)
expenseRepo.listByOwner.mockResolvedValue(...)
cardItemRepo.createForOwner.mockResolvedValue(...)

// Root cause: vi.mock factory produces typed mock objects but TypeScript
// widens the type to the exact factory return, stripping vi.fn() methods.
```

## Why This Is a Blocker vs a Note

- **Is a blocker** when `corepack pnpm typecheck` fails on these lines — the validation gate must pass cleanly.
- **Is NOT a runtime product bug** — tests pass at runtime; the product behavior is correct.
- **The fix** is adding a cast at the call site: `(method as ReturnType<typeof vi.fn>).mockImplementation(...)`.

## Pre-Existing Test File Pollution

This error type can also appear in **other test files** (e.g., `cf-e2-s2-stabilization.test.ts`) that were written before this story's test patterns were established. Those are pre-existing errors relative to the current story but still block `typecheck`. The fix for pre-existing incomplete mock objects is to complete the return shape with all Prisma fields — never leave `as any` casts on mock returns that should be fully typed.

## CF-E2-S3 Example

See `references/cardforge-vitest-vi-mock-type-widening-2026-05-29.md` in `bmad-dev-story` for the full fix pattern and field-completion guidance for Sale/CardItem mocks.