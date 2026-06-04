# CF-E1-S6: Negative Profit Crash in Dashboard (2026-05-25)

- **Trigger**: loss-making analytics (negative gross/net profit, negative per-platform/set/card/lot profit) crash `/dashboard` because `formatGbp()` rejects negative pence.
- **Root cause**: `toPence` in `src/lib/money/index.ts` threw on negative values; `formatGbp` depended on it; dashboard and breakdowns passed negative profit through `formatGbp`.

## Fix

- `toPence(value)`:
  - Stays non-negative; used for amounts (revenue, COGS, etc.).
- `toPenceAllowNegative(value)`:
  - New; used for profit/loss/margin.
- `formatProfitGbp(pence)`:
  - New; formats profit/loss:
    - Positive/zero: "£12.34"
    - Negative: "-£12.34"
- DashboardClient:
  - Use `formatProfitGbp` for:
    - Gross Profit
    - Net Profit
    - All breakdown profit values (platform, set, card, lot).

## Regression Tests

- formatProfitGbp:
  - Positive, zero, negative.
  - Rejects non-numeric input.
- toPenceAllowNegative:
  - Allows negative; rejects invalid.
- calcDashboardMetrics:
  - Loss-making scenario: COGS + expenses > revenue → negative netProfitPence; verify formatProfitGbp does not throw.
- calcPlatformBreakdown:
  - Loss-making platform → negative profitPence; verify formatProfitGbp does not throw.

## Usage

- Load when:
  - Implementing or correcting analytics, profit/COGS, or GBP formatting.
  - Reviewing a dashboard or export that can show negative profit.
- Use this as a checklist:
  - Are profit/loss values allowed negative?
  - Are they using a formatter that won’t throw on negatives?
  - Is there a regression test for a loss-making scenario?
