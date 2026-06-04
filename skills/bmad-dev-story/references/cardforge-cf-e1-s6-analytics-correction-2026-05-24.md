# CF-E1-S6 Analytics Correction — Reference (2026-05-24)

Used when:
- You are doing bmad-dev-story or bmad-code-review on CardForge analytics, HMRC exports, or COGS/profit logic.
- You see review findings like:
  - “COGS uses cardItem.quantity instead of sale quantity”
  - “Gross/net profit omit fees/shipping”
  - “Breakdowns not wired into /dashboard”
  - “No focused analytics/export tests”

Key corrections (concrete, not abstract):

1) COGS must use sale-level quantities

- WRONG:
  - Collect soldCardIds from filtered sales.
  - For each cardItem in soldCardIds:
    - COGS += cost_basis_pence * cardItem.quantity.
- RIGHT:
  - For each COMPLETED sale in filter:
    - qty = sale.quantity
    - cost = cardItem.cost_basis_pence (by sale.cardItemId)
    - COGS += cost * qty

2) Gross profit must include fees

- WRONG:
  - gross_profit = revenue - COGS
- RIGHT:
  - gross_profit = revenue - COGS - (platform_fee + payment_fee)

3) Net profit must include shipping cost and expenses

- WRONG:
  - net_profit = gross_profit - expenses
- RIGHT:
  - net_profit = gross_profit - shipping_cost - expenses

4) Margin formula

- Use:
  - margin = (net_profit / (revenue + shipping_charged)) * 100
  - or 0 if denominator = 0
- Keep this consistent between:
  - calcDashboardMetrics()
  - MARGIN_SUMMARY export logic in export.service.ts

5) Dashboard breakdowns must be wired

- If calcCardBreakdown / calcLotBreakdown exist but are not used:
  - Call them in the dashboard server page (e.g., /dashboard/page.tsx).
  - Pass results into DashboardClient.
  - Render “By Card” and “By Lot” sections.

6) Export download route

- The App Router route for CSV is /exports/download (from /exports/download/route.ts).
- Client components must build URLs to /exports/download?... not /dashboard/exports/download?...

7) Tests

- For any analytics/export story, add a focused test file (e.g., analytics-and-exports.test.ts) that:
  - Tests calcDashboardMetrics with:
    - Multiple sale quantities.
    - Fees and shipping.
  - Tests date/platform filters.
  - Tests breakdown grouping.
  - Tests CSV row shapes and source IDs.
  - Tests export route handler rejects invalid exportType.
