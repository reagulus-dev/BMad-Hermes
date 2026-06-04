# CardForge Analytics Negative Profit Display Review

Use this note when reviewing analytics/dashboard/export stories that introduce profit, margin, or profitability breakdowns.

## Pitfall

A corrected profit formula can legitimately produce negative values. If the UI formats those values through a money helper that validates inputs as non-negative persisted money, a loss-making period can crash the dashboard instead of rendering a negative GBP amount.

Concrete CardForge example:

- `formatGbp()` calls `toPence()`.
- `toPence()` rejects negative values with `Negative money value not allowed` because it is designed for persisted money inputs.
- CF-E1-S6 dashboard metrics and breakdowns can produce negative `grossProfitPence`, `netProfitPence`, or `profitPence` after COGS, fees, shipping cost, and expenses.
- Rendering those through `formatGbp()` blocks the story even when the formulas and static validation pass.

## Review checklist

When profit/loss values are rendered:

1. Identify which pence fields can be negative:
   - gross profit
   - net profit / net contribution
   - platform/card/lot/set profitability
   - margin numerator or contribution fields
2. Inspect display helpers, not just formula helpers:
   - If a helper is intended for non-negative persisted money, do not assume it is safe for derived profit/loss values.
   - Look for `toPence()`, `min(0)` validators, or schemas that reject negative values.
3. Require a safe display path for derived signed money:
   - e.g. `formatSignedGbp()` / `formatProfitGbp()` or local formatting that handles `-£x.xx` / `£-x.xx` consistently.
4. Check signed percentage display too, not only GBP display:
   - A loss-making period can produce a negative `marginPct` with a positive denominator.
   - Do not accept UI logic such as `marginPct > 0 ? "x%" : "—"`; it hides required negative margin values instead of rendering them honestly.
   - Reserve `—` for genuinely unavailable/no-denominator states, not for negative but valid margins.
5. Require focused regression coverage for at least one loss-making metric or breakdown row and, when margin is story-required, one negative-margin display/formatting path.
6. Do not pass solely because typecheck/lint/build/tests pass if existing tests only cover profitable happy paths.

## Verdict guidance

Use `BLOCKED` when an explicit dashboard/profitability AC can crash or hide loss-making business data.

Use `PASS WITH NOTES` only if:

- the signed display path is safe,
- focused loss-making display coverage exists, and
- remaining concerns are only copy/polish or runtime QA deferrals.
