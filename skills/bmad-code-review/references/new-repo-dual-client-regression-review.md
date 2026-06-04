# New-Repo Dual-Client Regression Review (CardForge CF-E5-S6 round-2 / round-3 pattern)

## Why this reference exists

A new repo module (`src/lib/db/job-repo.ts` for the CF-E5-S6 background-job
model) opened `prisma.$transaction(async (tx) => { ... })` at three call
sites instead of `prismaDirect.$transaction(...)`. The full Vitest suite
passed 472/472. The wrong-client usage was hidden because the unit-test
mock for the new repo only aliased `prisma`, not `prismaDirect`. The
Dev Agent Record explicitly promised the opposite contract
("no `$transaction` writers in the jobRepo") and the implementation
contradicted the contract.

This is a class of regression that will recur every time a new repo
module is added to a CardForge-style Supabase + Prisma + Vercel Lambda
project. Capture the detection pattern here so the next review catches
it on the first pass, not the second.

## The three-line detection checklist

For every NEW repo module that opens `$transaction`, verify all three:

1. **The new repo uses `prismaDirect.$transaction(...)`**, not
   `prisma.$transaction(...)`. Grep for `prisma\.\$transaction` in the
   new file. The CF-E5-S5 carry-forward rule is global, not scoped to
   `owner-scope.ts`.

2. **The unit-test mock has a distinct `prismaDirect` mock surface**
   (preferred), or at minimum aliases `prismaDirect: mockPrisma`
   alongside `prisma: mockPrisma`. Distinct `vi.fn()` instances for
   each client's `$transaction` (CF-E5-S6 round-3 pattern) are the
   strongest guard — see "The stronger guard" section below. The
   minimum acceptable pattern in
   `tests/unit/sales-service.test.ts:36` and
   `tests/unit/cf-e5-s3-multi-location-stock.test.ts:92`:

   ```ts
   vi.mock("@/lib/db/prisma", () => {
     const mockPrisma = {
       // ... model fields ...
       $transaction: vi.fn(),
     };
     return { prisma: mockPrisma, prismaDirect: mockPrisma };
   });
   ```

   When the mock is shaped this way AND the production code calls
   `prismaDirect.$transaction`, the wrong-client usage fails at test
   time (the call lands on the wrong mock field, or the typed
   mock object raises a TS2339 on `prismaDirect.$transaction`).
   When the mock is shaped without the `prismaDirect` alias, both
   `prisma` and `prismaDirect` resolve to the same `mockPrisma` and
   the wrong-client usage is silent.

3. **The Dev Agent Record's "no `$transaction` writers" claim matches
   the implementation.** A "no `$transaction` writers in the new repo"
   line in the carry-forward / Dev Agent Record is a live constraint.
   If the implementation uses `$transaction`, the diff either re-routes
   to `prismaDirect` or amends the contract with a rationale. A
   contradicting contract is a blocker: the next session that trusts
   the carry-forward will reproduce the wrong-client usage.

## Concrete failure shape (CardForge CF-E5-S6 round 2)

Production:

```ts
// src/lib/db/job-repo.ts (round-2)
// Line 243
const result = await prisma.$transaction(async (tx) => {
  const current = await tx.job.findFirst({
    where: { id: jobId, owner_id: oid, status: "RUNNING" },
    select: { id: true, total_rows: true, processed_rows: true },
  });
  if (!current) return 0;
  if (current.processed_rows + chunkSize > current.total_rows) return 0;
  await tx.job.update({
    where: { id: jobId },
    data: {
      processed_rows: current.processed_rows + chunkSize,
      last_tick_at: new Date(),
    },
  });
  return 1;
});
```

```ts
// src/lib/db/job-repo.ts (round-2)
// Line 276, 345 — same pattern, different helpers
return prisma.$transaction(async (tx) => { /* … */ });
```

Test mock (the silent-coercion shape):

```ts
// tests/unit/job-repo.test.ts
vi.mock("@/lib/db/prisma", () => {
  return {
    prisma: {
      job: {
        create: vi.fn<() => Promise<unknown>>(),
        findFirst: vi.fn<() => Promise<unknown>>(),
        // …
        update: vi.fn<() => Promise<unknown>>(),
        updateMany: vi.fn<() => Promise<{ count: number }>>(),
      },
      cardItem: { findMany: vi.fn<() => Promise<unknown[]>>() },
      cardItemLocation: { findMany: vi.fn<() => Promise<unknown[]>>() },
      $transaction: vi.fn(),
      // ← NO prismaDirect alias
    },
  };
});
```

In the production code, the round-2 job repo imported only `prisma`
(`import { prisma } from "./prisma";` — line 13 of `job-repo.ts`). The
production `$transaction` call therefore resolved to the pooler-bound
client. The unit test passed because the mock surface had no
`prismaDirect` field to typecheck against; the call landed on the
mocked `prisma.$transaction` regardless of which client production
code meant to use.

Result: 472/472 tests pass, the diff looks correct in isolation, and
the first live Vercel tick will hit P2028 on the second statement
inside the `BEGIN`/`COMMIT` envelope (the same connection-reuse race
CF-E5-S5 was designed to fix).

## Why unit tests cannot catch this (without the stronger guard)

The `vi.mock("@/lib/db/prisma", …)` factory in this codebase returns
a single object. The module is a singleton in the test process. When
production code imports `prisma` and `prismaDirect` from
`@/lib/db/prisma`, both names resolve to the SAME mock object. The
mock cannot distinguish "production code asked for the pooler client"
from "production code asked for the transaction-safe client" — the
`$transaction` call lands on the same `vi.fn()` regardless.

The only ways to make a passing test run meaningful for the
dual-client split are:

1. **Shape the mock with both aliases pointing at the same object.**
   The wrong-client usage is then a TYPE error: if production code
   uses `prisma.$transaction` and the typed mock object has no
   `$transaction` field on `prismaDirect` (or vice versa), TS2339
   fires. This requires the mock to be typed tightly enough that
   TypeScript checks field access per alias.

2. **Use two distinct mock objects** for `prisma` and `prismaDirect`,
   then assert that each call site invokes the correct one. This
   catches the wrong-client usage at test time as a
   `expect(...).toHaveBeenCalled()` mismatch. **This is the
   preferred pattern for any new repo on the dual-client split** —
   see "The stronger guard" below.

3. **Add a wiring test** that imports `@/lib/db/prisma` at runtime
   and asserts `prisma !== prismaDirect` and that `prismaDirect` is
   bound to a transaction-safe URL (no `pgbouncer=true`, port 5432).
   The pattern in `tests/unit/prisma-dual-client.test.ts` is the
   template.

The CF-E5-S6 round-2 mock uses (1) but the production code uses
`prisma.$transaction` (not `prismaDirect.$transaction`), so the
TS2339 guard does not fire (in practice, the mock object is cast
`as unknown as { ... }` to escape strict PrismaClient typing, and
the cast strips the typecheck guard anyway). The right shape for a
new repo is (2) — distinct mock objects with explicit wiring tests —
so the wrong-client usage fails at test time, not at runtime in
production. The suggested `prismaDirect: mockPrisma` aliasing
pattern (1) is the minimum acceptable guard; it works only when
the test surface is freshly written and types are kept tight.

## The stronger guard: distinct `vi.fn()` instances + wiring tests (CF-E5-S6 round-3)

Option (1) above (the `prismaDirect: mockPrisma` aliasing pattern) is
the existing CardForge convention. It works only when the mock's
TypeScript types are tight enough that the wrong client field access
fails typecheck. In practice, the mock object is almost always cast
`as unknown as { ... }` to escape strict PrismaClient typing, and
the cast strips the typecheck guard. With that cast, the runtime
`vi.fn()` is the same object for `prisma.$transaction` and
`prismaDirect.$transaction`, and no assertion can distinguish
"production called the right one" from "production called the
wrong one".

The stronger guard, verified by `tests/unit/job-repo.test.ts` after
the CF-E5-S6 round-3 correction landed (2026-06-03):

```ts
vi.mock("@/lib/db/prisma", () => {
  // DISTINCT $transaction fns so a wrong-client usage is observable
  // at test time, not just at typecheck time.
  const prismaTransaction = vi.fn();
  const prismaDirectTransaction = vi.fn();
  return {
    prisma: {
      job: { /* ... */ },
      $transaction: prismaTransaction,
    },
    prismaDirect: {
      job: { /* ... */ },
      $transaction: prismaDirectTransaction,
    },
  };
});
```

Then add a `dual-client wiring (P2028 regression guard)` describe
block that proves the production code calls the right client:

```ts
describe("dual-client wiring (P2028 regression guard)", () => {
  it("mock factory exposes distinct prisma and prismaDirect $transaction fns", () => {
    expect(prismaMock.$transaction).not.toBe(prismaDirectMock.$transaction);
  });

  it("advanceProgressBeforeRun calls prismaDirect.$transaction, not prisma.$transaction", async () => {
    prismaDirectMock.$transaction.mockImplementation(async () => 0);
    await jobRepo.advanceProgressBeforeRun(1, 42, 50);
    expect(prismaDirectMock.$transaction).toHaveBeenCalledTimes(1);
    expect(prismaMock.$transaction).not.toHaveBeenCalled();
  });
  // … one wiring test per $transaction helper …
});
```

With distinct instances, the assertions are concrete: if a future
change accidentally writes `prisma.$transaction(...)` in any of the
helpers, the corresponding wiring test fails with "expected
`prisma.$transaction` not to have been called, but it was called
1 times". The next code-review pass catches the regression at
unit-test time, not at runtime in production.

**Trade-off**: this requires updating all existing `$transaction`
test bodies to seed `prismaDirectMock` rather than `prismaMock`
inside the `mockImplementation` callback, because production code's
`tx` argument is now `prismaDirect`'s transaction client. The
mechanical migration:

- `prismaMock.$transaction.mockImplementation(async (fn) => …)` →
  `prismaDirectMock.$transaction.mockImplementation(async (fn) => …)`
- `prismaMock.job.findFirst.mockResolvedValue(...)` inside the
  callback → `prismaDirectMock.job.findFirst.mockResolvedValue(...)`
- `return fn(prismaMock);` → `return fn(prismaDirectMock);`

The mechanical migration is the only cost. The benefit is a
runtime check that fires on the first wrong-client regression, not
the second.

**Patch-tool collision pitfall** when applying this migration via
`patch` with `replace_all=true`: a `prismaMock.job.X.mockResolvedValue`
pattern may match the WRONG line (e.g. a line that should be
`prismaDirectMock.job.Y.mockResolvedValue` and a different field).
If the patch's old_string is too short, the .replace_all corrupts
the file silently. Always restore from a known-good backup (e.g.
`git show HEAD~0:tests/unit/job-repo.test.ts > /tmp/old.ts`) before
applying the migration, and do the migration one describe block at
a time with full-context `old_string` rather than a single
`replace_all`. The CF-E5-S6 round-3 session hit this exact failure
shape and recovered from a `cp` of the round-2 baseline.

## What to do when this regression is found

Tight bmad-dev-story correction (preferred, CF-E5-S6 round-3 shape):

1. Change `import { prisma } from "./prisma";` to
   `import { prisma, prismaDirect } from "./prisma";` in the new repo.

2. Change every `prisma.$transaction(async (tx) => { ... })` to
   `prismaDirect.$transaction(async (tx) => { ... })`. Reads and
   single-statement writes stay on `prisma`.

3. Update the new repo's unit-test mock to expose BOTH `prisma` and
   `prismaDirect` with DISTINCT `vi.fn()`-backed `$transaction`
   instances (the "stronger guard" pattern above). Update every
   existing `$transaction` test body to seed `prismaDirectMock` and
   pass `prismaDirectMock` as the `tx` arg.

4. Add a `dual-client wiring (P2028 regression guard)` describe block
   with one wiring test per `$transaction` helper that asserts
   `prismaDirect.$transaction` was called and `prisma.$transaction`
   was not. This makes a future wrong-client regression fail at
   test time, not at runtime.

5. Rerun the validation bundle (`prisma:validate`, `typecheck`,
   `lint --max-warnings=0`, full Vitest, `build`, `git diff --check`).

6. The dual-client wiring test in `tests/unit/prisma-dual-client.test.ts`
   should still pass; it asserts the two clients are distinct and
   that `prismaDirect` is bound to a transaction-safe URL.

Minimum acceptable correction (the existing convention, weaker):

1. Same as above steps 1, 2, 5, 6.

2. Update the new repo's unit-test mock to alias
   `prismaDirect: mockPrisma` alongside `prisma: mockPrisma`. The
   alias forces TypeScript to flag a future regression that
   re-introduces `prisma.$transaction` (the typed mock object
   surfaces the missing-field error) — **only when the mock's
   types are kept tight**. The `as unknown as { ... }` cast
   universally used in this codebase strips this guard.

Then a fresh `bmad-code-review` per the standard BLOCKED → correction
→ re-review cycle.

## Verdict-shaping language for the review writeup

When this regression is the single blocker, the review writeup
should be tightly scoped so the correction is small and mechanical:

> "Round 1's 4 blockers (non-atomic tick claim, crash-after-write,
> failed-create counter, merge retry idempotency) are properly
> addressed in the round-2 diff. The single new blocker:
> `src/lib/db/<new-repo>.ts` opens `prisma.$transaction` at N call
> sites instead of `prismaDirect.$transaction`. This re-introduces
> the CF-E5-S5 P2028 race against the Supabase Transaction Pooler
> and contradicts the round-2 Dev Agent Record promise that
> `<new-repo>` uses `prisma` (pooler) for reads and single-statement
> writes only. The unit-test mock for `<new-repo>` does not alias
> `prismaDirect`, so the wrong-client usage is hidden from the
> N/N passing test run.
>
> Required next action: `bmad-dev-story` correction for
> `<STORY-ID>` (switch `prisma.$transaction` to
> `prismaDirect.$transaction` in `<new-repo>.ts`; alias
> `prismaDirect` in the `<new-repo>` test mock), then fresh
> `bmad-code-review`."

This is the CardForge CF-E5-S6 round-2 BLOCKED template, generalised.

## Related references

- `prisma-supabase-transaction-pooler-p2028.md` — the original
  symptom/root-cause/fix class reference. Establishes the
  `prismaDirect` requirement and the mock-aliasing pattern for
  EXISTING repos. This file extends that pattern to NEW repos that
  are introduced after the dual-client split is in place.
- `client-polled-background-job-review.md` — the broader
  claim/progress/idempotency review checklist for any background-job
  story. The dual-client regression is a separate concern that
  applies to any new repo, not just background-job repos.
