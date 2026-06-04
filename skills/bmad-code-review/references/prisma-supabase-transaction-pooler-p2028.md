# Prisma + Supabase Transaction Pooler + Serverless Race (P2028)

## Symptom

Production CSV import (or any other multi-step write path using
`prisma.$transaction(async (tx) => { ... })`) returns:

```
PrismaClientKnownRequestError:
Invalid prisma.cardItem.create() invocation:
Transaction API error: Transaction not found. Transaction ID is invalid,
refers to an old closed transaction Prisma doesn't have information
about anymore, or was obtained before disconnecting.
code: 'P2028'
```

…while the same code works fine in local dev and in the local test
suite. The CSV import's individual queries succeed; only the ones
inside the `$transaction` callback fail.

## Root cause (verified)

PgBouncer in transaction-mode (the only mode Supabase exposes on port
6543) handles one Postgres `BEGIN`/`COMMIT` envelope per pooled
connection. Prisma's interactive `$transaction(async (tx) => { ... })`
API issues `BEGIN`, runs the callback queries on whatever physical
connection the pool hands back, and issues `COMMIT`.

On a long-lived Node server, the same connection is reused for the
full transaction and it works. On Vercel Lambda (or any serverless
runtime that caches a global Prisma client across invocations), the
cached `PrismaClient` may be invoked across different physical
connections inside the same transaction window. The pool re-assigns a
fresh connection on the second query, that connection has no `BEGIN`
context, and Postgres returns `P2028`.

This is a known incompatibility class between Prisma's interactive
transaction API and pgbouncer transaction-mode under serverless
connection reuse, NOT a code bug. Unit tests pass because they run
against a local DB or test connection pool, not the live Supabase
transaction pooler.

## Why it was always latent

Multi-step `$transaction` write paths (CSV chaos-sort merge, atomic
quantity + bucket replacement, sales create/update/delete with COGS
deduction) are introduced in normal feature work and exercised by
unit tests. The Vitest suite runs against a local/test database
connection. Smoke tests typically cover only authenticated page loads
and dialog reachability, not the actual `$transaction` write path
against the live pooler. The first time the live Vercel deployment
hits the import path is the first time P2028 surfaces — and the
fix has to be deployed before any user can import.

## Fix: dual Prisma client

In `src/lib/db/prisma.ts` (or equivalent), keep the existing `prisma`
client bound to `DATABASE_URL` (the transaction pooler) for read paths
and single-statement writes. Add a second `prismaDirect` client bound
to `DIRECT_URL` (the direct DB connection on port 5432). The direct
connection is the only mode where the `BEGIN`/`COMMIT` envelope
survives the full transaction window on a serverless client.

Then route every `prisma.$transaction(async (tx) => { ... })` call
site to `prismaDirect.$transaction(...)`. Reads and single-statement
writes stay on the pooler. Direct connections exhaust Supabase's
15-conn limit quickly under serverless load, so do NOT route read
paths through `prismaDirect`.

Concrete file boundaries in a CardForge-style project:

- `src/lib/db/prisma.ts`: dual client export + `assertDirectUrl`
  runtime guard that rejects `pgbouncer=true` or port 6543 in
  `DIRECT_URL` so a future env misconfiguration re-introduces P2028
  with a loud error instead of a silent regression.
- `src/lib/db/owner-scope.ts` and any other repo helper that opens
  `$transaction`: switch to `prismaDirect.$transaction(...)`. The
  pre-flight invariant guards (e.g., `sum(bucket.quantity) ==
  CardItem.quantity`) stay BEFORE the transaction; the transaction
  is the atomicity wrapper, not the validator.
- `prisma/schema.prisma`: `directUrl = env("DIRECT_URL")` is already
  declared (Prisma Migrate uses it for schema DDL). No schema change
  needed; production must set `DIRECT_URL` to the Supabase direct
  connection (`db.<ref>.supabase.co:5432`).
- `.env.example`: document both URLs and the dual-client split.

## Runtime guard

The existing `assertProductionPooler` runtime guard verifies that
`DATABASE_URL` is on the transaction pooler (port 6543,
pgbouncer=true, connection_limit=1) so the existing pool-exhaustion
protection stays. Add a complementary `assertDirectUrl` guard that:

- Logs `DIRECT_URL` shape on boot (sanitized; replace `:user:pass@`
  with `:USER:PASS@`).
- Throws in production if `DIRECT_URL` includes `pgbouncer=true`
  (the pgbouncer transaction-mode races with `$transaction`, so
  pointing `prismaDirect` at the same pooler re-introduces P2028).
- Throws in production if `DIRECT_URL` targets port 6543 (same
  reason).

The guard's error messages must be string-matched by a unit test
(`assertDirectUrl regex`) so a future guard text edit forces the test
update.

## Test surface

The local Vitest suite cannot exercise the live pooler, so the
P2028 regression is not catchable in unit tests. The right test
strategy:

1. **Wiring test** (new, in `tests/unit/`): assert that the prisma
   module exports distinct `prisma` and `prismaDirect` clients, that
   both are `PrismaClient` instances with `$transaction` methods,
   and that the two guards throw on misconfigured env vars. This
   catches typos in the module export surface and in the guard
   regex.
2. **Mock factory update** (in any existing test that mocks
   `@/lib/db/prisma`): export `prismaDirect` aliased to the same
   `mockPrisma` object so existing `expect(prisma.<model>).toHaveBeenCalled()`
   assertions remain valid. Forgetting this alias causes every test
   that exercises a `$transaction` call site to fail with "No
   'prismaDirect' export is defined on the '@/lib/db/prisma' mock."
3. **Live production smoke** (e2e, opt-in): a Playwright spec
   gated on `RUN_PROD_SMOKE=1` that signs in, uploads a small CSV
   with unique-prefixed identity keys, and asserts the response
   contains "created" but not "P2028". This is the only verification
   that the dual-client split actually restores the live
   production `$transaction` path. It must be opt-in because it
   mutates production data.

The local e2e dev-server attempt to run a `cf-e5-s4-runtime-smoke`
spec (or any spec that depends on live Supabase seed data) is not
sufficient: the dev server can reach the live Supabase, but the
spec's React-hydration wait times out differently under
`pnpm dev` than under a Vercel build. AC #N for "live spec still
passes" must be re-verified by the operator against the Vercel
deploy, not by a dev-env run.

## Carry-forward notes

- Future shutdown/cleanup stories must `await prisma.$disconnect()`
  AND `await prismaDirect.$disconnect()`. The current
  PrismaClient cache in `globalThis` covers both, but explicit
  shutdown paths must disconnect both pools.
- If Supabase ever exposes a session-mode pgbouncer on port 6543
  with `pool_mode=session`, the dual-client pattern can be
  simplified by pointing `prismaDirect` at the same pooler. The
  runtime guard must be updated to allow that shape; do not
  "fix" it in a future story without the assertion changes.
- `prismaDirect` MUST NOT be used for high-frequency read paths.
  Direct connections exhaust Supabase's 15-conn limit quickly
  under serverless load. If a future read path needs `$transaction`
  semantics without write mutation (rare), prefer refactoring to
  a single-statement query or batching at the action layer
  instead of routing reads through `prismaDirect`.
- **NEW repo introduced after the dual-client split is in place.**
  The "every `$transaction` call site routes to `prismaDirect`"
  rule applies to NEW repos, not just `owner-scope.ts`. A new
  repo that opens `prisma.$transaction` will silently re-introduce
  P2028; a unit-test mock that does not alias `prismaDirect` will
  hide the regression behind a passing test run. See
  `references/new-repo-dual-client-regression-review.md` for the
  concrete pattern and the CardForge CF-E5-S6 round-2 BLOCKED
  example.
