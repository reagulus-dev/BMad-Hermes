---
name: bmad-stowsy-date-only-and-expenses-wiring
description: Fix Stowsy regressions where item-entry dates drift backward by a day and Expenses buckets spend by created timestamps instead of purchase dates.
version: 1.0.0
author: Alice
license: MIT
metadata:
  hermes:
    tags: [stowsy, dates, timezone, expenses, react-native, expo, supabase, sqlite]
    related_skills: [systematic-debugging, bmad-dev-story, bmad-evidence-reporting]
---

# BMad Stowsy Date-Only and Expenses Wiring

Use when Stowsy shows any of these symptoms:
- purchase date or expiry date moves back a day
- pressing `Today` stores the previous date
- reopening a picker changes the selected date
- Expenses totals/category breakdown feel miswired to insertion time instead of purchase time

## Root causes to check first

1. UTC date-only regression in item-entry forms
- Bad patterns:
  - `new Date().toISOString().split('T')[0]`
  - `date.toISOString()` for picker selections
  - picker values created from `new Date(dateOnly + 'T00:00:00')`
- In positive-offset timezones (BST, Asia, etc.), UTC midnight conversion can shift the calendar date backward.

2. Expenses period anchored to creation time instead of purchase time
- Anonymous flow may use `createdAt`
- Signed-in flow may use `created_at`
- Correct period anchor should be `purchaseDate` / `purchase_date` first, with created timestamp only as fallback

## Canonical fix pattern

### A. Introduce shared local date-only helpers
Create/update `src/shared/utils/dateOnly.ts` with helpers equivalent to:
- `toLocalDateOnly(date: Date): string`
- `localTodayDateOnly(now?: Date): string`
- `isoToDateOnly(value)`
- `dateOnlyToPickerDate(value)` using local midday, not UTC midnight
- `dateOnlyToNoonUtcIso(value)` for save-boundary persistence
- `formatDateOnlyDisplay(value)`

Key rule:
- Form state should stay as local `YYYY-MM-DD`
- Convert to ISO only at persistence boundaries
- Use noon UTC (`T12:00:00.000Z`) rather than midnight UTC to avoid date rollback

### B. Rewire all item-entry surfaces consistently
Audit these files first:
- `src/app/add-item.tsx`
- `src/app/edit-item/[id].tsx`
- `src/app/scan/manual-entry/index.tsx`
- `src/app/scan/barcode-result/index.tsx`

Apply the same rules everywhere:
- `today` default uses `localTodayDateOnly()`
- picker `onChange` stores `toLocalDateOnly(date)`
- display uses `formatDateOnlyDisplay(...)`
- picker `value` uses `dateOnlyToPickerDate(...)`
- save payload uses `dateOnlyToNoonUtcIso(...)`
- auto-estimated expiration dates from `estimateExpirationDate(...)` should be normalized with `toLocalDateOnly(...)`, not `toISOString().split('T')[0]`

### C. Fix Expenses period logic
Audit `src/app/(tabs)/expenses.tsx`

For both anonymous and signed-in flows:
- fetch rows with both price/quantity and date fields
- compute an `effectiveDate`
  - anonymous: `purchaseDate ?? createdAt`
  - signed-in: `purchase_date ?? created_at`
- bucket current/previous period rows in JS using `effectiveDate`
- keep `created*` only as fallback, not primary anchor

## Verification gates

Run:
- `cd /home/reagulus/projects/stowsy && npm run type-check`
- `cd /home/reagulus/projects/stowsy && npx jest tests/unit/itemEntryDateSource.test.ts tests/unit/expensesWiringSource.test.ts tests/unit/expensesPremiumSource.test.ts tests/unit/expensesUtils.test.ts --runInBand`

## Recommended regression guards

Add/update source tests that explicitly fail if code reintroduces:
- `new Date().toISOString().split('T')[0]` as a date-only default in item-entry screens
- `date.toISOString()` for picker-selected local dates
- Expenses queries filtered directly by `createdAt` / `created_at` as the primary spend anchor

Suggested tests:
- `tests/unit/itemEntryDateSource.test.ts`
- `tests/unit/expensesWiringSource.test.ts`

## Evidence to report honestly

Good completion report should state:
- which files were rewired
- that the root cause was UTC/local calendar drift
- that Expenses was using created timestamps instead of purchase dates
- exact verification commands and PASS results
- whether runtime/on-device verification was or was not performed

## Pitfalls

- Fixing only one screen is not enough; drift can survive in edit/manual/barcode flows
- `new Date('YYYY-MM-DD')` and `toISOString().split('T')[0]` are not interchangeable with local calendar intent
- A UI that looks correct can still have miswired Expenses period logic underneath
- Do not claim full closure without distinguishing source/test verification from hardware runtime verification
