# Millipence Migration Pattern (CF-E3)

When migrating money precision (e.g. pence ×100 → millipence ×1000 for 3-decimal accuracy):

## Checklist

1. **Schema**: create a single `UPDATE ... SET col = col * 10` migration SQL for every monetary column.
2. **Money helpers**: rename functions (`gbpToPence` → `gbpToMillipence`, `toPence` → `toMillipence`, etc.) and update divisor (`/100` → `/1000`, `*100` → `*1000`).
3. **Server actions**: update all `gbpToPence()` calls to `gbpToMillipence()`.
4. **UI inputs**: change `step="0.01"` → `step="0.001"` on all money number inputs.
5. **UI display**: change all `/100).toFixed(2)` → `/1000).toFixed(3)` and `*100` → `*1000` in onChange handlers.
6. **Analytics**: update `calcSaleProfit` field names (`salePricePence` → `salePriceMillipence`, etc.) and all call sites.
7. **CSV export**: update `penceToGbp` → `millipenceToGbp` with 3 DP.
8. **Tests**: multiply every hardcoded money value by 10 and update expected format strings (`"£12.34"` → `"£12.340"`).
9. **Prisma field names**: keep `*_pence` column names — they are just labels; the values are in millipence after migration.
10. **Run full test suite** before claiming done. All existing tests should still pass.

## Pitfalls

- **Do not rename Prisma columns** — that requires a second migration. The `*_pence` suffix is acceptable; only the values change.
- **Apply DB migration BEFORE code deploys** — otherwise the app reads pence values as millipence (off by 10×).
- **Search comprehensively** for `/ 100` and `* 100` — they hide in defaultValue expressions, onChange handlers, and format helpers.
- **Test values multiply by 10** — every `500` (5.00 GBP in pence) becomes `5000` (5.00 GBP in millipence).
- **Format strings need 3 DP** — `"£0.00"` → `"£0.000"`, `"£12.34"` → `"£12.340"`.
