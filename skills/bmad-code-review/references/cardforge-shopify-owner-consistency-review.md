# CardForge Shopify owner-consistency review pattern

Use this when reviewing additive marketplace/Shopify foundation stories that add owner-scoped tables for connections, listings, allocations, webhook events, or future sync state.

## Session signal

In CF-E4-S1, the initial implementation correctly added `owner_id` columns and RLS policies to each Shopify table, but child rows could still reference another owner's rows through plain integer FKs:

- `ShopifyListing.owner_id = attacker`, `connection_id = victim_connection_id`
- `ShopifyListingAllocation.owner_id = attacker`, `card_item_id = victim_card_item_id`
- `ShopifyWebhookEvent.owner_id = attacker`, `connection_id = victim_connection_id`

RLS that checks only the child row's own `owner_id` does not prevent this if the database relation allows cross-owner references.

## Review checklist

For each new owner-scoped child table:

1. Identify every relation to another owner-scoped table.
2. Verify the child row cannot point to a parent/resource owned by someone else.
3. Prefer DB-level composite enforcement, not comments or application-only assumptions.
4. Add a focused regression test or schema-integrity test that asserts the owner-consistency contract remains present.

## Correction pattern

In Prisma:

```prisma
model ParentTable {
  id       Int @id @default(autoincrement())
  owner_id Int

  @@unique([id, owner_id])
}

model ChildTable {
  id        Int @id @default(autoincrement())
  owner_id  Int
  parent_id Int

  parent ParentTable @relation(fields: [parent_id, owner_id], references: [id, owner_id], onDelete: Cascade)
}
```

In migration SQL:

```sql
CREATE UNIQUE INDEX "parent_id_owner_id_key"
    ON "parent_table"("id", "owner_id");

ALTER TABLE "child_table"
    ADD CONSTRAINT "child_parent_owner_fkey"
    FOREIGN KEY ("parent_id", "owner_id")
    REFERENCES "parent_table"("id", "owner_id")
    ON DELETE CASCADE ON UPDATE CASCADE;
```

For allocation tables, apply this to every referenced owner-scoped resource, for example:

- `(connection_id, owner_id) -> shopify_connections(id, owner_id)`
- `(listing_id, owner_id) -> shopify_listings(id, owner_id)`
- `(card_item_id, owner_id) -> card_items(id, owner_id)`

## Verdict guidance

- **BLOCKED** if owner-scoped child rows can cross-reference another owner's connection/listing/card item and the story claims owner-scoped persistence/security foundation.
- **PASS WITH NOTES** if the gap is corrected during review, validation is rerun, and artifacts explicitly record that live DB migration deployment/RLS smoke is still unverified.

## Validation bundle used in CF-E4-S1

- `corepack pnpm run prisma:validate`
- `corepack pnpm run prisma:generate`
- `corepack pnpm run typecheck`
- `corepack pnpm run lint`
- `corepack pnpm run test`
- `corepack pnpm run build`
- `git diff --check`

Do not write credential-like placeholder database URLs into durable artifacts; if a dummy URL is needed for validation, record it as `DATABASE_URL=[REDACTED] ...`.
