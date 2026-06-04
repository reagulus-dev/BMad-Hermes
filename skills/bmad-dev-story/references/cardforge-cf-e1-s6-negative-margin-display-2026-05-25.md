# CF-E1-S6: Negative margin hidden as "—" (2026-05-25)

- Issue:
  - calcDashboardMetrics() can produce a negative marginPct for a loss-making period.
  - DashboardClient previously used:
    - marginPct > 0 ? "${...}%" : "—"
  - This hid legitimate negative margins (e.g., -46.7%) as "—", violating the analytics story AC.

- Fix:
  - Updated condition to:
    - marginPct !== 0 ? `${marginPct.toFixed(1)}%` : "—"
  - So:
    - Positive: "30.8%"
    - Negative: "-46.7%"
    - Zero/no data: "—"

- Test pattern:
  - Added regression tests that:
    - Use a loss-making sale input (COGS + fees + costs > revenue).
    - Confirm:
      - calcSaleProfit returns negative marginPct.
      - A UI-mirrored rendering expression shows "-X.Y%", not "—".

- Design rule:
  - "—" means no data; negative is still data. Never use "—" to hide negative financials.
