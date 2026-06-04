# CardForge analytics + HMRC export review pattern

Use for CardForge/Next.js stories that add dashboard metrics, profitability breakdowns, CSV exports, or HMRC-friendly reporting over Prisma-owned sales/inventory/expenses data.

## Review checks

- Treat analytics formulas as product correctness, not display polish.
- For dashboard and summary/export calculations, inspect COGS/profit source code directly:
  - COGS for sold cards must be based on the filtered sale quantity per sale, not the current `CardItem.quantity` remaining in inventory.
  - If the same card appears in multiple sales, each sale line must contribute its own quantity and revenue/cost contribution.
  - Profit semantics must explicitly account for sale price, sale quantity, platform fee, payment fee, shipping charged, shipping cost, linked card cost basis, and expenses according to the story contract.
  - Avoid duplicating formula logic between dashboard helpers and export services; if duplicated, compare both paths because one can regress while the other passes.
- Verify every story-named breakdown is actually rendered/reachable, not only implemented as a pure helper:
  - Platform breakdown
  - Lot breakdown
  - Set breakdown
  - Card profitability breakdown
  - A helper such as `calcCardBreakdown()` or `calcLotBreakdown()` is insufficient if the page only fetches/renders platform/set rows.
- Compare dashboard/export profit formulas against the existing sale-level money helper before accepting focused tests:
  - In CardForge, `calcSaleProfit()` treats `shipping_charged_pence` as revenue-side: `grossRevenue + shippingCharged - fees - shippingCost - COGS`.
  - Block dashboard or margin-summary implementations that include shipping charged only in the margin denominator while omitting it from net profit.
  - Do not accept tests that merely encode the inconsistent formula; require tests that prove alignment with the canonical sale-profit helper.
- Review each rendered “profit” breakdown for formula consistency, not just presence:
  - Platform, card, lot, and set profitability should either allocate sale-level fees/shipping consistently or clearly label themselves as revenue-minus-COGS/non-profit summaries.
  - Block when UI copy says profitability/profit but formulas omit required fees or shipping semantics from the story contract.
- For HMRC COGS/inventory exports that claim a selected date range, verify the export branch actually uses `fromDate`/`toDate`:
  - A current-inventory dump that ignores the selected period is misleading when the story says revenue, COGS, expenses, and summary exports are over a selected date range.
  - Either implement period-scoped COGS rows from sales/card links or explicitly re-scope the UI/story copy so it does not claim period filtering for inventory snapshots.
- Owner-scope evidence must exercise a practical boundary:
  - A route test that rejects invalid query params before service/data access does not prove owner-scoped analytics/export behavior.
  - Prefer tests that mock `resolveCurrentOwnerId()` and repository calls or call the production service/route path far enough to assert the owner id flows into data reads.
- Check App Router route-group paths carefully:
  - A file under `src/app/(dashboard)/exports/download/route.ts` is served as `/exports/download`, not `/dashboard/exports/download`.
  - Client download/navigation code must target the public route path produced by the route tree, not the route-group folder name.
  - Build output listing dynamic routes is good evidence for the actual path.
- Require focused tests when the story says analytics/export evidence is part of the completion contract:
  - Calculation tests for revenue, AOV, COGS, expenses, gross/net profit, and margin.
  - Date and platform filter tests.
  - Breakdown grouping tests for platform, lot, set, and card profitability.
  - CSV row-shape tests including source record IDs (`sale.id`, `cardItem.id`, `lot.id`, `expense.id`, summary anchors as applicable).
  - Route/service boundary tests where practical, especially owner-scoped reads and invalid filter handling.

## Verdict guidance

Use `BLOCKED` when:

- COGS/profit uses current inventory quantity instead of sale quantity.
- Required fee/shipping semantics are omitted from profit calculations.
- A story-named breakdown exists only as an unused helper and is not surfaced in the dashboard.
- CSV/download UI targets a non-existent route because a route-group segment was treated as a URL segment.
- Required focused analytics/export tests are absent, even if broad typecheck/lint/build passes.

Use `PASS WITH NOTES` only when formulas, route reachability, and required focused tests are sound, but runtime browser smoke, live Supabase/RLS, or founder QA remain deferred gates.
