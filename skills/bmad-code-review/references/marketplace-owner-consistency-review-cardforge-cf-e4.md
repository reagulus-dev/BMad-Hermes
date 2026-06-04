# Marketplace owner-consistency review pattern (CardForge CF-E4)

Use this when reviewing additive marketplace/channel tables in a Prisma + Supabase/Postgres app where each table has its own `owner_id` plus foreign keys to connections, listings, inventory rows, webhook events, or allocations.

## Pitfall

Rows can look owner-scoped because every table has `owner_id` and RLS checks the row's `owner_id`, while still allowing a child row to reference another owner's parent/resource by guessed integer ID.

Examples:

- `ShopifyListing.owner_id = attacker` with `connection_id = victim_connection_id`.
- `ShopifyListingAllocation.owner_id = attacker` with `card_item_id = victim_card_item_id`.
- `ShopifyWebhookEvent.owner_id = attacker` with `connection_id = victim_connection_id`.

RLS that only checks the child row's `owner_id` does not catch this. App-level service filters are also not enough for a foundation/migration story that claims owner-scoped persistence.

## Review requirement

For each child table that has both `owner_id` and a related-row foreign key, verify DB-level owner consistency through one of these patterns:

1. Composite unique keys on parents/resources, e.g. `@@unique([id, owner_id])`.
2. Composite foreign keys from child to parent/resource, e.g.:
   - `ShopifyListing(connection_id, owner_id) -> ShopifyConnection(id, owner_id)`
   - `ShopifyListingAllocation(listing_id, owner_id) -> ShopifyListing(id, owner_id)`
   - `ShopifyListingAllocation(card_item_id, owner_id) -> CardItem(id, owner_id)`
   - `ShopifyWebhookEvent(connection_id, owner_id) -> ShopifyConnection(id, owner_id)`
3. A DB trigger/check/RPC boundary that enforces the same invariant and is covered by tests.

Prefer composite FKs for additive schema foundations when practical; they are explicit, durable, and reviewable in both Prisma schema and migration SQL.

## Evidence to ask for

- `prisma validate` passes after composite relation changes.
- Migration SQL contains composite unique indexes and composite FKs, not only ID-only FKs.
- Focused regression test or schema-integrity test asserts the owner-consistency contract is present.
- Story/review notes distinguish this static DB-integrity evidence from live Supabase migration deployment.

## Verdict guidance

- **BLOCKED** if a current story claims owner-scoped marketplace persistence but child rows can reference another owner's connection/listing/inventory rows.
- **PASS WITH NOTES** if the schema/migration/test contract enforces owner consistency, but live migration deployment or live marketplace behavior is out of scope/unverified.
