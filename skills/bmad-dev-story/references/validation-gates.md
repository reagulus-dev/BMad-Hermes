# Validation Gates Reference

## Standard Gate Sequence

Run in order. Stop on first failure unless the failing test is explicitly pre-existing and unrelated.

```bash
corepack pnpm typecheck
corepack pnpm lint
corepack pnpm test
corepack pnpm build
# prisma validate requires DATABASE_URL — if .env is absent or empty, use a valid-format placeholder:
DATABASE_URL='postgresql://placeholder:***@localhost:5432/placeholder' corepack pnpm exec prisma validate
git diff --check
```

> **Schema tests**: `node --experimental-vm-modules vitest run tests/unit/<story-slug>-schemas.test.ts` — only run directly when the file exists. If no schema test was created for the story, this gate is skipped silently.

## Action Return Contract

All actions used in `action={}` form attributes **must** return `Promise<void>`. Do not return typed result objects from server actions wired to forms.

## Owner Scoping Pattern

Always use `resolveCurrentOwnerId()` from `@/lib/auth/owner-resolver`. Never hardcode `ownerId = 1`.

## GBP Money Handling

- All persisted money: integer pence (no decimals).
- Convert £→pence on submission via `gbpToPence()` or equivalent.
- Use `toPence()` for non-negative amounts; `toPenceAllowNegative()` for profit/loss.
- Use `formatProfitGbp()` for any UI that can show negative profit.

## Native Dialog Usage

For edit/create dialogs in dashboard components, prefer the native HTML `<dialog>` element over custom modal overlays.

## Prisma-as-Type Pattern

Use Prisma model types directly in client components (no intermediate custom types) unless there is a clear reason to wrap.

## Expense Archive

Use `expenseRepo.archiveById(id)` (soft archive), not hard `delete`.

## Zod Schema

Zod schema enums do not need separate enum imports in actions files — import the schema only.

## Large Stabilization Stories (e.g., CF-E2-S2)

When a story has many acceptance criteria across multiple areas (UX, E2E, edge cases):

- Use execute_code with batch patching (multiple patch() calls) to apply changes across many files in one shot. This is faster and more reliable than many separate terminal commands.
- For unit tests touching analytics/calculations:
  - Prefer testing the pure calculation functions directly (e.g., calcSaleProfit, formatProfitGbp) with concrete inputs.
  - Avoid heavy mocking of Prisma/Supabase in unit tests unless necessary — the existing analytics-and-exports tests already cover those patterns.
  - If you must mock, mirror the exact mock structure used in existing tests (e.g., analytics-and-exports.test.ts) rather than inventing your own.
- For E2E tests:
  - Write them as Playwright specs that follow the same patterns as mvp-smoke.spec.ts.
  - Use the same test user credentials pattern (unique email per test suite).
  - Validate empty states, confirmations, and form validation via DOM assertions, not visual inspection.

## sprint-status.yaml Pitfall

Indentation matters. Patch can corrupt YAML. **Prefer write_file (full rewrite)** over patch for this file.
