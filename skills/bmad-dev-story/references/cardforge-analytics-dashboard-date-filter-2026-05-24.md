# CardForge analytics date filter — server/client Date serialization (CF-E1-S6)

## Pattern: Date handling between Next.js server page and client component

Server pages that accept date filters via `searchParams` parse dates with `z.coerce.date()`. The parsed `Date` objects flow to client components but TypeScript prohibits `Date | null | undefined` from being assigned to `string | null | undefined` (even though both are valid JSON).

**Solution**: serialize to ISO date-string in the server component before passing to the client:

```typescript
// dashboard/page.tsx (server component)
const parsed = analyticsDateFilterSchema.safeParse(rawFilters);
const filter = parsed.success ? parsed.data : {};

const serializableFilter = {
  fromDate: filter.fromDate ? filter.fromDate.toISOString().split("T")[0] : undefined,
  toDate: filter.toDate ? filter.toDate.toISOString().split("T")[0] : undefined,
  platform: filter.platform ?? undefined,
};

// Pass serializableFilter (string | undefined) to client component, not filter (Date | null | undefined)
return <DashboardClient metrics={metrics} activeFilter={serializableFilter} />;
```

## Client component filter type

```typescript
type FilterProps = {
  fromDate?: string;   // ISO date string "YYYY-MM-DD" or undefined
  toDate?: string;     // ISO date string "YYYY-MM-DD" or undefined
  platform?: string;   // "EBAY" | "CARDMARKET" | "FACEBOOK" | "OTHER" or undefined
};
```

## Prisma validate without .env

If `DATABASE_URL` is absent or empty (no `.env` committed), `prisma validate` fails with:

```
Error validating datasource `db`: the URL must start with the protocol `postgresql://` or `postgres://`.
```

**Solution**: pass a valid-format placeholder:

```bash
DATABASE_URL='postgresql://placeholder:placeholder@localhost:5432/placeholder' corepack pnpm exec prisma validate
```

This is safe for schema validation — the placeholder URL is only used for driver-connectivity validation, not actual DB operations.