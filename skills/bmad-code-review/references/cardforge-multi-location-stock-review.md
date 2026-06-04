# CardForge CF-E5-S3 multi-location stock review blockers

Use this reference when reviewing inventory/location-bucket stories that remove or replace a legacy single-row `location` field with a per-bin/bucket model.

## Blocker patterns found

### 1. Removed field still exposed through sort/filter controls

If a story drops `CardItem.location` (or any equivalent legacy column), review every UI/query path that can still name that field indirectly:

- Zod/filter schemas that accept `sortBy: "location"` or similar.
- Table headers/components that generate `sortHref("location")`.
- Repository helpers that blindly translate `filters.sortBy` into Prisma/SQL `orderBy: { [sortBy]: ... }`.

If the field was removed from Prisma/schema but a URL/control can still send it as an order key, treat as **BLOCKED**. Correct by either disabling/removing that sort, mapping it to a real bucket-derived sort, or rejecting/ignoring it safely, with a focused regression test.

### 2. Identity fields computed but not persisted

For CSV/import dedupe semantics, verify that every field in the logical identity key is also normalized and persisted on create paths.

CardForge example:

- `importCsvToLotAction` computed identity with `language` and `finish_type`.
- `pendingCreates.push(...)` omitted `language`/`finishType`.
- Result: non-default rows classified as JP/reverse/etc. but persisted as Prisma defaults (`EN`/`REGULAR`).

Treat this as **BLOCKED** when the story claims logical identity includes those fields. Require focused tests for at least one non-default language and one non-default finish import.

### 3. Total quantity and bucket replacement must be one stock mutation

When a model keeps `CardItem.quantity` as canonical total and `CardItemLocation` rows as per-bin breakdown, any user action/import merge that changes both must be atomic at the story boundary.

Block if code does:

1. `cardItem.update({ quantity })`
2. then separately `replaceBucketsForCardItem(...)`

Even if the bucket replacement helper has its own transaction, a failure after the quantity update can break `sum(buckets) == CardItem.quantity`. Prefer a single repo/service transaction that updates the parent quantity and replaces buckets together, plus a focused transaction-shape/failure test.

## Review checklist

- Search schema/filter/table code for removed field names and indirect sort/filter keys.
- Compare logical import identity construction with actual create/update payloads.
- Check create, merge, skip, and duplicate modes separately.
- Confirm focused tests cover non-default identity dimensions, not only defaults.
- For aggregate invariants (`sum(children) == parent.total`), inspect transaction boundaries across parent + child writes, not just each helper in isolation.
