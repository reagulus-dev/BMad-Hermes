# CF-E5-S6 — Hobby-Safe Background-Job CSV Import (Vercel Hobby plan)

**Date**: 2026-06-03
**Story**: `bmad-dev-story` for CF-E5-S6
**Vercel plan**: Hobby (no cron, no minute-resolution scheduled tasks)
**Outcome**: 453/453 tests pass, 4 new test files, 3 new API routes, dialog rewritten; live Vercel 10k-row re-verification is the operator action post-deploy.

## The architectural fix

A 10k-row CSV import on Vercel's 300s hard maxDuration:
- 200 sequential 50-row chunks × ~3s Vercel→Supabase eu-west-1 RTT = ~600s of wall-clock work inside one synchronous Server Action.
- Vercel kills the lambda at 300.00s; the in-flight chunk is rolled back; half the rows landed.
- The CF-E5-S5 fix (dual Prisma client) is correct and stays. The structural failure is that the import is a single synchronous Server Action whose wall-clock exceeds the Vercel limit by 2x.

The Hobby-safe pivot: move the import off the synchronous Server Action runtime and onto a background-job model where each invocation is short (≤3s wall-clock per tick). The Vercel Hobby plan only restricts cron — short fetch requests are fine. The chain is "self-resubmitting" via the dialog's 2s poll cycle, not a Vercel cron tick.

## Hobby-safe pattern: client-poll-driven tick

The dialog's 2s `setInterval` polls `GET /api/csv-import/jobs/[id]`. On each poll, if the polled `lastTickAt` is older than ~3.5s and the job is still `PENDING` or `RUNNING`, the dialog fires `POST /api/csv-import/tick` to advance one chunk. The runner runs one chunk (≤3s wall-clock), updates the Job row, and returns. The dialog's next poll picks up the new state.

The submit route does NOT arm a setTimeout chain — Vercel would kill the lambda and the chain would die. The chain is the dialog's poll cycle. If the operator closes the browser, the job stops advancing; reopening the page re-arms. This is the Hobby-plan trade-off.

## Job model + RLS

```prisma
model Job {
  id              Int       @id @default(autoincrement())
  owner_id        Int
  type            JobType
  status          JobStatus @default(PENDING)
  total_rows      Int
  processed_rows  Int       @default(0)
  created_rows    Int       @default(0)
  merged_rows     Int       @default(0)
  skipped_rows    Int       @default(0)
  error_count     Int       @default(0)
  payload         Json     // { csvText, lotId, duplicateMode, existingByIdentity, bucketsByCardId, costPerCardPence, idempotencyKey }
  error_rows      Json      @default("[]")
  error_message   String?
  started_at      DateTime?
  completed_at    DateTime?
  last_tick_at    DateTime?
  created_at      DateTime  @default(now())
  updated_at      DateTime  @updatedAt

  userProfile     UserProfile @relation(fields: [owner_id], references: [id], onDelete: Cascade)

  @@index([owner_id, status, type])
  @@index([status, last_tick_at])
  @@map("jobs")
}
```

Two indexes serve two queries:
- `[owner_id, status, type]` — the dialog's mount-time poll fetches the active job for the owner.
- `[status, last_tick_at]` — the resume sweep fetches stale-RUNNING jobs ordered by `last_tick_at ASC`.

RLS follows the `20260528000002_enable_rls_and_security_hardening` pattern (owner_id resolved from `auth.uid()` via the `user_profiles.auth_uid` join). The composite shape is the documented MVP-safe pattern across all owner-scoped tables.

## Atomic counter increment with terminal transition

`jobRepo.recordChunkProgress` opens a `prisma.$transaction` (NOT `prismaDirect` — single-statement writes only), reads the canonical `processed_rows` and `error_rows`, computes the next state, and updates the row in one atomic call. The status transitions to `COMPLETED` when `processed_rows + chunk_size >= total_rows`. Error rows are appended with a 1000-entry cap to bound storage growth on huge CSVs.

## Reusing the existing write paths

The runner is a pure function that calls the existing `cardItemRepo.createManyWithInitialBucketsForOwner` and `cardItemRepo.applyMergeStockForOwner`. The chaos-sort semantics, the no-bucket seed correction (CF-E5-S3 round-3), and the `prismaDirect` 5432 transaction client (CF-E5-S5) are preserved verbatim. We do NOT introduce a second import path or a second set of bucket-write helpers.

The runner re-parses the CSV from `payload.csvText` per tick. Parsing a 10k-row CSV is sub-second on Vercel, so the re-parse cost is dwarfed by the per-chunk repo writes. The alternative (store parsed rows on the payload) bloats the JSONB column unnecessarily.

## Back-compat shim for existing tests

The legacy `importCsvToLotAction(formData)` is preserved as a synchronous back-compat shim. It delegates to the same `runImportCore` shared with the async path. This keeps `tests/unit/csv-import-large-batch.test.ts` (CF-E5-S5) green — the existing 6/6 large-batch regression still exercises the synchronous round-trip end-to-end.

```ts
// The action file structure:
async function runImportCore(ownerId, csvText, lotId, duplicateMode) { /* shared work */ }
export async function importCsvToLotAction(formData) { /* back-compat shim for tests */ }
export async function submitCsvImportAction(input) { /* new async submit */ }
export async function getCsvImportJobAction(input) { /* new status poll */ }
```

## Dialog: localStorage recovery + poll cycle

```tsx
// localStorage key for the active job
const ACTIVE_JOB_KEY = "cardforge.inventory.activeCsvJob";

// Poll cadence
const POLL_INTERVAL_MS = 2000;
const TICK_FRESHNESS_MS = 3500;

// On mount, recover any active job from localStorage. A hard refresh
// during an import does not lose the job; the dialog resumes polling.
useEffect(() => {
  const raw = window.localStorage.getItem(ACTIVE_JOB_KEY);
  if (raw) {
    const parsed = JSON.parse(raw) as ActiveJobState;
    if (parsed && typeof parsed.jobId === "number") {
      setActiveJob(parsed);
    }
  }
}, []);

// Polling effect: when an active job is present, poll every 2s.
// On each poll, fire a tick request if the last_tick_at is older
// than 3.5s (i.e. no tick in flight recently).
useEffect(() => {
  if (!activeJob) return;
  const tick = async () => {
    const snap = await fetchJob(activeJob.jobId);
    if (!snap) { clearActiveJob(); return; }
    setJobSnapshot(snap);
    const lastTick = snap.lastTickAt ? new Date(snap.lastTickAt).getTime() : 0;
    if ((snap.status === "PENDING" || snap.status === "RUNNING") &&
        Date.now() - lastTick > TICK_FRESHNESS_MS) {
      await runTick(activeJob.jobId);
      const after = await fetchJob(activeJob.jobId);
      if (after) setJobSnapshot(after);
    }
    if (snap.status === "COMPLETED" || snap.status === "FAILED" || snap.status === "CANCELLED") {
      router.refresh();
    }
  };
  void tick();
  const handle = window.setInterval(() => void tick(), POLL_INTERVAL_MS);
  return () => window.clearInterval(handle);
}, [activeJob, fetchJob, runTick, router, clearActiveJob]);
```

## API route shape

| Route | Method | Auth | Body | Response |
| --- | --- | --- | --- | --- |
| `/api/csv-import/jobs` | POST | required | `{ csvText, lotId, duplicateMode, idempotencyKey? }` | `{ jobId, totalRows, validationErrors, started, ownerId }` |
| `/api/csv-import/jobs/[id]` | GET | required | — | `{ id, status, totalRows, processedRows, ... }` |
| `/api/csv-import/tick` | POST | required | `{ jobId }` | `{ jobId, status, processedRows, totalRows, done, ... }` |

All routes use `requireAuthedOwnerId()` for owner resolution. Cross-owner ids surface as 404 (not 403, so existence is not leaked). The tick route is idempotent on terminal jobs (no double-processing).

## Defense in depth: resumeStaleRunning

Every tick calls `jobRepo.resumeStaleRunning(5 * 60 * 1000)` to reset any RUNNING job whose `last_tick_at` is older than 5 minutes back to PENDING. This is a safety net for a tick that crashed mid-chunk: the next tick re-claims the job and continues from `processed_rows`. The Vercel Hobby plan does not have a cron-equivalent background trigger, so the dialog's poll cycle is the only one to call this — but the sweep is also useful for any future migration to Vercel Pro + cron.

## Soft idempotency

`POST /api/csv-import/jobs` accepts an optional `idempotencyKey` (caller-generated, e.g. `${Date.now()}-${random}`). The submit action's `findActiveByIdempotencyKey` returns the existing jobId if a PENDING/RUNNING job carries the same key. The check is by `payload.idempotencyKey` (JSONB lookup) because the v1 has no UNIQUE index. A hard `UNIQUE(owner_id, idempotency_key)` index is a follow-up. This prevents a double-click from creating two jobs.

## Five scope questions resolved (founder's Hobby-safe pivot)

1. **Vercel plan**: Hobby confirmed. **No cron**. The chain is the dialog's 2s poll cycle.
2. **Tick frequency**: 2s dialog poll + 3.5s freshness threshold = roughly one tick every 3.5–5.5s per active import.
3. **Cancel UX**: **None**. Once submitted, an import runs to completion. The pill shows progress; the result view re-opens on click. A future story could add a POST `/api/csv-import/jobs/[id]/cancel` route and a `markCancelled` job-repo helper.
4. **Result-view placement**: **Dialog re-opens on pill click**. No new `/inventory/imports/[id]` page.
5. **Idempotency key**: **Soft check**. `X-Idempotency-Key` is supported; a hard UNIQUE index is a follow-up.

## Test pattern: source-grep dialog test

The story spec calls for a dialog test that asserts the founder-visible promise closure (the in-dialog warning at line 215-218 is removed). Without `@testing-library/react` as a project dep, a source-grep test is the right level:

```ts
// tests/unit/csv-import-dialog-async.test.ts
import { readFileSync } from "fs";
import { join } from "path";

const source = readFileSync(join(__dirname, "..", "..", "src", "app", "(dashboard)", "inventory", "_components", "CsvImportDialog.tsx"), "utf8");

it("does not contain the legacy in-dialog warning", () => {
  expect(source).not.toMatch(/row-by-row progress needs the future background-job importer/);
});
```

The full source-grep test (8 assertions) verifies: no legacy warning, no legacy import, submit goes through fetch to /api/csv-import/jobs, localStorage key present, pill copy correct, POLL_INTERVAL_MS = 2000, tick route present, no cancel route (Hobby-safe: no cancel UX).

## Carry-forward

- **Migration history**: apply the new `prisma/migrations/20260603000000_add_job_table/migration.sql` to the live Supabase database before the CF-E5-S6 code deploys. Add the row to `_prisma_migrations` if applied outside `prisma migrate deploy`.
- **Dual-client wiring preserved**: every CF-E5-S3 `$transaction` call site continues to route through `prismaDirect`. The job repo (createForOwner, getForOwner, listActiveForOwner, recordChunkProgress, markRunning, markFailed, resumeStaleRunning) uses `prisma` (pooler) — single-statement writes only.
- **Hobby-plan limitation**: imports progress only while a client is polling. Closing the browser stops the job until the page re-opens. The `lastTickAt` heartbeat means the dialog knows when to fire a tick on resume.
- **Live runtime verification**: the architectural change requires a live Vercel 10k-row CSV re-verification post-deploy. Apply the migration, submit the CSV, expect the job to reach `processed_rows == total_rows == 10000` within ~10–20 minutes. `[prisma:direct] ... isPort5432=true hasPgbouncer=false` in logs (CF-E5-S5 wiring preserved).
- **Future polish story** could add: a hard `UNIQUE(owner_id, idempotency_key)` index on `Job`, a `GET /api/csv-import/jobs?status=active` endpoint for cross-session recovery, a `POST /api/csv-import/jobs/[id]/cancel` route + `markCancelled` helper, a Vercel Pro upgrade to add minute-resolution cron as the tick trigger (the dialog's poll cycle would still work as a backstop).
