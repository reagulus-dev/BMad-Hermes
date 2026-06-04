# CardForge marketplace-channel foundation pattern (CF-E4-S1)

Use this when adding a new marketplace/channel foundation (Shopify/eBay/Cardmarket-style expansion) to CardForge without implementing live external sync yet.

## Safe foundation scope

- Keep the new channel additive and disabled/no-op until config and a later connection story exist.
- Do not add required channel-specific fields to existing core business models (`CardItem`, `Sale`, `Lot`, `Expense`, `ExportRun`).
- Add the new channel to `SalePlatform` and every browser-safe platform list used by operator UI/filtering, not just the sale creation form. In CF-E4-S1 this included both sales UI and dashboard platform options.
- Add a protected dashboard shell route only after the route exists, then add sidebar navigation.
- Add config guard tests for missing/blank/complete env values.
- Add schema tests proving create/update sale validation accepts the new channel while existing platforms still pass.

## Inventory/listing identity rule

CardForge `CardItem` rows are internal stock buckets, not permanent marketplace listings. Chaos sorting can create multiple rows for the same public sale identity solely because physical stock lives in different locations.

Future marketplace publishing should therefore model:

```text
Public marketplace listing / variant
  -> allocations back to one or more CardItem rows
```

Do not make a one-`CardItem`-row-to-one-public-listing schema assumption. Location should normally remain internal fulfillment metadata; sale identity is based on card identity plus sale-relevant attributes such as language, condition, finish, edition/variant, set/card number.

## Shopify-hosted storefront foundation

For Shopify specifically:

- Shopify hosts public products, collections, cart, checkout, and payment.
- CardForge remains private inventory, publishing, order reconciliation, profit, and HMRC ledger.
- Foundation story should not implement OAuth, Admin API calls, product publishing, webhook routes, or live checkout/order verification.
- Persist future idempotency state early (`ShopifyWebhookEvent`) even if webhook routes are deferred.
- Prefer `ShopifyListing` + `ShopifyListingAllocation` over direct `card_item_id` on the listing.

## Validation and artifact notes

- Run the normal BMad gates: Prisma validate/generate, typecheck, lint, unit tests, build, `git diff --check`.
- If an extra live DB probe such as `prisma migrate status` fails due remote reachability, record it as non-gate evidence when live migration deployment is out of scope. Do not let it override passed local gates.
- After implementation, mark the story `implemented_not_reviewed` and route to `bmad-code-review`, not completion.
