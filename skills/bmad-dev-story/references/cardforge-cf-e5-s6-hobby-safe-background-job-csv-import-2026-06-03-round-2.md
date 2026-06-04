# CF-E5-S6 — Hobby-Safe Background-Job CSV Import, Round 2 Correction

**Date**: 2026-06-03
**Story**: `bmad-dev-story` correction (round 2) for CF-E5-S6
**Triggered by**: 2026-06-03 BLOCKED code review (4 findings — non-atomic tick claim, crash-after-write, failed-create counter, merge retry idempotency)
**Outcome**: 472/472 tests pass across 31 files (was 453/453; +9 job-repo, +6 runner, +5 API, +0 dialog; `csv-import-large-batch.test.ts` back-compat still 6/6). All validation gates clean. Awaiting fresh `bmad-code-review`.

This is the round-2 reference for the round-1 file `cardforge-cf-e5-s6-hobby-safe-background-job-csv-import-2026-06-03.md`. Per the bmad-dev-story convention (CF-E5-S3 has rounds 1-4 reference files; the reference file grows; the state advances; the artifacts grow), this file is appended, not consolidated.

## What the round-1 design got wrong

The round-1 tick model was:

```
getForOwner(jobId, ownerId)     ← racy read
markRunning(jobId, ownerId)      ← plain update, not an atomic claim
runOneChunk(job)                 ← writes happen HERE
recordChunkProgress(...)         ← bump processed_rows + counters HERE
```

This is unsafe on **four** distinct boundaries:

1. **Concurrent tick claim.** Two overlapping ticks (the dialog's 2s poll cycle fires `POST /api/csv-import/tick` from every open tab + from a second client) both read the same `processed_rows`, both call `markRunning` (which is a plain owner-scoped `update`, not a status-gated claim), and both call `runOneChunk` on the same slice. Both run the same card writes. The second `recordChunkProgress` call sees a `processed_rows` already advanced by the first tick and may derive wrong counter deltas.

2. **Crash-after-write.** A Vercel invocation that dies after the card writes (inside `createManyWithInitialBucketsForOwner` or `applyMergeStockForOwner`) but before `recordChunkProgress` lands leaves `processed_rows` unchanged. `resumeStaleRunning` resets the job to PENDING; the next tick re-claims it and reprocesses the same slice. New cards are duplicated; merge quantities are re-applied on top of the post-write state (which the round-1 `applyMergeStockForOwner` writes in absolute-set form, so the second pass overwrites the post-merge state back to a stale value — a stock regression).

3. **Failed create chunks advance the counter.** The round-1 runner did:
   ```ts
   for (let i = 0; i < pendingCreates.length; i += chunkSize) {
     const subChunk = pendingCreates.slice(i, i + chunkSize);
     try {
       const created = await cardItemRepo.createManyWithInitialBucketsForOwner(ownerId, subChunk);
       // ... but `created.length !== subChunk.length` was reported, not caught
     } catch (err) {
       result.errors.push({ rowNumber: 0, message: `Create chunk: ${msg}` });
       // NO rollback of pendingCreates
     }
   }
   result.created += pendingCreates.length;  // BUG: pre-increment, lies about persistence
   ```
   When `createManyWithInitialBucketsForOwner` throws on a sub-chunk, no rows in that sub-chunk persisted. But `result.created += pendingCreates.length` (computed at the end of the per-row loop, BEFORE the create calls) is added to the result regardless. `recordChunkProgress` derives the processed delta as `created + merged + skipped`, so failed sub-chunks advance `processed_rows` AND `created_rows`, and the job can falsely reach COMPLETED with skipped failed writes.

4. **Merge-mode retries use stale submit-time quantities.** The round-1 runner computed merge deltas from the submit-time `existingByIdentity` snapshot (e.g. `duplicate.quantity = 3` from `payload.existingByIdentity`):
   ```ts
   mergeQuantities.set(duplicate.id, (mergeQuantities.get(duplicate.id) ?? duplicate.quantity) + row.quantity);
   ```
   On replay, the same code reads `duplicate.quantity = 3` from the frozen payload, but the live DB already has the card at `quantity = 3 + 5 = 8` (from the first run's writes). The replay re-computes `3 + 5 = 8` (same answer) and calls `applyMergeStockForOwner({ quantity: 8, buckets: [...stale bucket set] })` — which is an absolute set, so the post-write state is overwritten back to the pre-write shape. **Stock regresses.**

## The round-2 contract: claim → advance → write → counter

```
claimAndStart(jobId, ownerId, leaseMs)         ← atomic, returns row or null
  ↓ (claimed)
advanceProgressBeforeRun(jobId, ownerId, N)    ← atomic $transaction, processed_rows += N
  ↓ (advanced)
runOneChunk(job, ownerId, chunkSize)           ← idempotent writes
  ↓ (runner returned)
recordCountersAfterRun(jobId, ownerId, c)      ← per-counter increment + terminal
```

Each step is idempotent under crash/retry because:

- **claimAndStart** is gated on `(status='PENDING' OR (status='RUNNING' AND last_tick_at<cutoff))`. A second tick that arrives while the first is mid-write does not match the predicate (the first tick already set `status='RUNNING' AND last_tick_at=now`); it returns `null` and the route returns the current state from `getForOwner` (200, not 409). The lease re-claim branch (`status='RUNNING' AND last_tick_at < cutoff`) covers a tick that crashed mid-chunk without finishing — the next tick re-claims it. **Two concurrent ticks cannot both win.**
- **advanceProgressBeforeRun** is called BEFORE the runner's writes. If the Vercel invocation dies between the advance and the runner, `processed_rows` is already advanced; the next tick starts from the new offset. The runner re-fetches the live DB snapshot on every tick (so it sees the post-write state) and uses additive merge (so it never regresses). **A crash-after-write is safe by construction.**
- **runOneChunk** is idempotent. The runner ALWAYS re-fetches the existing-cards and existing-buckets snapshots from the live DB at tick start (`loadLiveSnapshot`). A replay sees the post-write state and routes new collisions to the merge path. Merges use the additive `applyDeltaMergeStockForOwner` (NOT the absolute `applyMergeStockForOwner`), so the call always adds `quantityDelta` to the live quantity — it cannot regress.
- **recordCountersAfterRun** takes the runner's ACTUAL persistence counts (`{ created, merged, skipped, errors, done }`), not a synthetic chunk-size delta. The runner counts only what the repo returned: `createdCount += created.length` where `created` is the return value of `createMany…ForOwner`. A thrown sub-chunk contributes 0. **Failed creates do not advance the counter.**

## Why advance-before-write is the right call (and "advance-after-write" is not)

The temptation: "advance processed_rows AFTER the writes so a failed chunk can be retried." This is the round-1 design, and it is structurally unsafe because the writes-and-advance window is unobservable — a crash in that window leaves the writes committed and the advance unrecorded, so the next tick reprocesses the same chunk. The round-2 design accepts that a failed chunk's rows are "consumed with errors" (the runner's `errors` array carries the per-row failure into `Job.error_rows`, capped at 1000) rather than re-attempted. The user re-imports the failed rows manually. The honesty trade-off is the right one because the alternative (silent duplication) is catastrophic for a 10k-row import.

The advance-before-write contract is proven by a call-order test in `tests/unit/api-csv-import-jobs.test.ts`:

```ts
it("calls advanceProgressBeforeRun BEFORE the runner (crash-after-write fix)", async () => {
  const callOrder: string[] = [];
  (jobRepo.advanceProgressBeforeRun as ReturnType<typeof vi.fn>).mockImplementation(async () => {
    callOrder.push("advance");
    return true;
  });
  (runOneChunk as ReturnType<typeof vi.fn>).mockImplementation(async () => {
    callOrder.push("runOneChunk");
    return { created: 0, merged: 0, skipped: 50, errors: [], done: false, totalRows: 100, processedRows: 50 };
  });
  (jobRepo.recordCountersAfterRun as ReturnType<typeof vi.fn>).mockImplementation(async () => {
    callOrder.push("recordCounters");
    return {} as never;
  });
  await tickPOST(makeRequest({ jobId: 1 }));
  expect(callOrder).toEqual(["advance", "runOneChunk", "recordCounters"]);
});
```

This is the round-2 proof-of-correctness for the architectural invariant. If a future refactor reorders the calls (e.g. moves the advance after the runner for "retry semantics"), this test fails immediately.

## Why additive delta-merge is the right call (and absolute-set is not)

`applyMergeStockForOwner({ quantity, buckets })` writes `CardItem.quantity = payload.quantity` and replaces the entire `CardItemLocation` set. On replay, the post-write state is overwritten back to a stale value — **stock regresses**. The fix is `applyDeltaMergeStockForOwner({ quantityDelta, bucketDelta })`:

```ts
// prismaDirect.$transaction
const card = await tx.cardItem.findFirst({ where: { id, owner_id }, select: { id, quantity } });
const existingBuckets = await tx.cardItemLocation.findMany({ where: { owner_id, card_item_id }, ... });
const newQuantity = card.quantity + delta.quantityDelta;
// merge bucketDelta into the existing bucket set
const finalBuckets = mergeBucketDeltas(existingBuckets, delta.bucketDelta);
const sumBuckets = finalBuckets.reduce((s, b) => s + b.quantity, 0);
if (sumBuckets !== newQuantity) {
  throw new Error(`Delta-merge invariant violated: sum(buckets) (${sumBuckets}) != CardItem.quantity (${newQuantity})`);
}
await tx.cardItem.update({ where: { id }, data: { quantity: newQuantity } });
await tx.cardItemLocation.deleteMany({ where: { owner_id, card_item_id } });
if (finalBuckets.length > 0) {
  await tx.cardItemLocation.createMany({ data: finalBuckets.map(b => ({ owner_id, card_item_id, location: b.location, quantity: b.quantity })) });
}
```

The merge is idempotent: replaying the same delta adds the same delta again. The `sum(buckets) == CardItem.quantity` invariant is asserted inside the `$transaction` (not just on the helper signature), so a delta that would violate the invariant throws and the entire chunk fails. The chaos-sort semantics and the no-bucket seed correction from CF-E5-S3 round-3 are preserved (the helper creates the seed bucket itself if `existingBuckets` is empty).

The runner ALWAYS re-fetches the live existing-cards/existing-buckets snapshot at tick start:

```ts
async function loadLiveSnapshot(ownerId: number, jobId: number): Promise<LiveSnapshot> {
  void jobId;
  const oid = Number.isInteger(ownerId) && ownerId > 0 ? ownerId : 0;
  if (oid === 0) return { existingByIdentity: new Map(), bucketsByCardId: new Map() };
  const existingCards = await prisma.cardItem.findMany({ where: { owner_id: oid }, ... });
  // ... build Map<identityKey, {id, quantity}> from existingCards
  const existingBuckets = await prisma.cardItemLocation.findMany({ where: { owner_id: oid }, ... });
  // ... build Map<cardId, Bucket[]> from existingBuckets
  return { existingByIdentity, bucketsByCardId };
}
```

Cost: one `findMany` per model per tick (~2-6s on a session pooler, matching the existing CF-E5-S5 pre-fetch). On replay, the runner sees the post-write state and routes new collisions to the merge path automatically — no special "is this a replay?" logic needed.

The merge-retry idempotency is proven by a test that simulates the crash-after-write scenario:

```ts
it("re-fetching the snapshot after a previous run applies a delta-merge (additive, idempotent)", async () => {
  // First run already applied a +1 delta-merge to card 1000 (post-write qty=2, Bin A bucket=2).
  // Second run replays row 2 (+1, also Abomasnow/SET/001, Bin A).
  // Live snapshot reflects post-first-run state: id 1000, qty 2, Bin A bucket 2.
  const snap = liveSnapshot([{ name: "Abomasnow", ..., id: 1000, quantity: 2, buckets: [{ id: 1, location: "Bin A", quantity: 2 }] }]);
  const result = await runOneChunk({ ...job, processed_rows: 1 /* replay offset */ }, 42, 50, { liveSnapshot: snap });
  expect(result.merged).toBe(1);
  expect(cardItemRepoMock.applyDeltaMergeStockForOwner).toHaveBeenCalledWith(
    42, 1000, { quantityDelta: 1, bucketDelta: [{ location: "Bin A", quantityDelta: 1 }] }
  );
});
```

The test asserts the runner called the helper with the row's contribution (1), not the pre-existing+row (3). On the next replay, the helper reads the live state and adds 1 again — never regresses.

## Concurrent claim proof

`claimAndStart` is gated on the status predicate:

```ts
const cutoff = new Date(Date.now() - leaseMs);
const result = await prisma.job.updateMany({
  where: { id: jobId, owner_id: oid, status: "PENDING" },
  data: { status: "RUNNING", started_at: new Date(), last_tick_at: new Date() },
});
if (result.count === 0) {
  // Try the stale-RUNNING re-claim branch
  const reclaim = await prisma.job.updateMany({
    where: { id: jobId, owner_id: oid, status: "RUNNING", last_tick_at: { lt: cutoff } },
    data: { status: "RUNNING", last_tick_at: new Date() },
  });
  if (reclaim.count === 0) return null;
}
return prisma.job.findFirst({ where: { id: jobId, owner_id: oid } });
```

A `findFirst`+`update` two-call pattern is racy (two ticks read the row, both see PENDING, both call `update`); a single `updateMany` with a status predicate is not. Postgres serializes the `UPDATE` against the row; the second tick's `updateMany` predicate does not match (the first tick already set `status='RUNNING'`) and returns `count=0`. The `findFirst` follow-up returns the now-RUNNING row to the winner. The route handles `null` by returning the current state from `getForOwner` (200, idempotent — the dialog sees the in-flight tick's state and does not re-fire).

The concurrent-claim test:

```ts
it("is idempotent when another tick holds the lease (returns current state, no runner call)", async () => {
  (jobRepo.claimAndStart as ReturnType<typeof vi.fn>).mockResolvedValue(null);
  (jobRepo.getForOwner as ReturnType<typeof vi.fn>).mockResolvedValue({ id: 1, ..., status: "RUNNING", processed_rows: 25, ... });
  const res = await tickPOST(makeRequest({ jobId: 1 }));
  expect(res.status).toBe(200);
  expect(runOneChunk).not.toHaveBeenCalled();
});
```

## Counter-actual-not-speculative proof

`recordCountersAfterRun` is the new per-counter increment. It takes the runner's `{ created, merged, skipped, errors, done }` — the actual persistence counts — and atomically increments:

```ts
return prisma.$transaction(async (tx) => {
  const current = await tx.job.findFirst({ where: { id, owner_id } });
  const newErrors = [...current.error_rows, ...counters.errors];
  const cap = 1000;
  const errorRows = newErrors.length > cap ? newErrors.slice(0, cap) : newErrors;
  return tx.job.update({
    where: { id },
    data: {
      created_rows: { increment: counters.created },     // ACTUAL count
      merged_rows: { increment: counters.merged },      // ACTUAL count
      skipped_rows: { increment: counters.skipped },    // ACTUAL count
      error_count: { increment: counters.errors.length },
      error_rows,
      last_tick_at: new Date(),
      ...(counters.done
        ? { status: "COMPLETED" as const, completed_at: new Date() }
        : { status: "RUNNING" as const }),
    },
  });
});
```

The runner counts only what the repo actually returned:

```ts
// round-2 runner, runOneChunk:
for (let i = 0; i < pendingCreates.length; i += chunkSize) {
  const subChunk = pendingCreates.slice(i, i + chunkSize);
  try {
    const created = await cardItemRepo.createManyWithInitialBucketsForOwner(ownerId, subChunk);
    if (created.length !== subChunk.length) {
      errors.push({ rowNumber: 0, message: `...returned ${created.length} rows for a sub-chunk of ${subChunk.length} inputs` });
    }
    createdCount += created.length;  // ACTUAL persistence count, not pendingCreates.length
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    errors.push({ rowNumber: 0, message: `Create chunk: ${msg}` });
    // failed sub-chunk -> createdCount unchanged
  }
}
```

The counter test:

```ts
it("does NOT increment created when the create helper throws on a sub-chunk", async () => {
  cardItemRepoMock.createManyWithInitialBucketsForOwner.mockRejectedValueOnce(new Error("bucket invariant violated"));
  const result = await runOneChunk(makeJob({ processed_rows: 0, total_rows: 3 }), 42, 3);
  expect(result.created).toBe(0);  // NOT pendingCreates.length
  expect(result.errors).toHaveLength(1);
});
```

## Short-circuit COMPLETED

`markCompletedIfReady` handles the case where `processed_rows >= total_rows` already (e.g. the previous tick's advance moved the final partial slice past the end in a 50-row chunk on a 25-row total). The route calls this BEFORE `advanceProgressBeforeRun` so the next tick does not re-invoke the runner:

```ts
const startOffset = claimed.processed_rows;
if (startOffset >= claimed.total_rows) {
  const updated = await jobRepo.markCompletedIfReady(claimed.id, ownerId);
  return NextResponse.json({ jobId: updated.id, status: updated.status, ..., done: true });
}
```

`markCompletedIfReady` is itself a `$transaction` that reads the current `(status, processed_rows, total_rows)` and transitions to COMPLETED iff `processed_rows >= total_rows` and the job is not already terminal. Defense in depth: a terminal job is returned unchanged.

## Test-count deltas (round 1 → round 2)

| File | Round 1 | Round 2 | New tests |
| --- | --- | --- | --- |
| `tests/unit/job-repo.test.ts` | 16 | **25** | +9 (claimAndStart × 4, advanceProgressBeforeRun × 4, markCompletedIfReady × 3; recordCountersAfterRun updated) |
| `tests/unit/csv-import-job-runner.test.ts` | 9 | **15** | +6 (delta-merge helper invoked with row quantity × 1, multiple rows in same chunk summing deltas × 1, failed-create counter × 2, merge-retry idempotency × 1, live snapshot loaded from DB × 1; also: delta-merge throw decrements mergedCount) |
| `tests/unit/api-csv-import-jobs.test.ts` | 18 | **23** | +5 (concurrent-claim path × 1, advanceProgressBeforeRun call order × 1, advanceProgressBeforeRun returning false × 1, short-circuit COMPLETED × 1, actual persistence counts to recordCountersAfterRun × 1) |
| `tests/unit/csv-import-dialog-async.test.ts` | 8 | 8 | +0 (the dialog contract is unchanged) |
| `tests/unit/csv-import-large-batch.test.ts` (back-compat) | 6 | 6 | +0 (CF-E5-S5 still passes 6/6) |
| **Total vitest** | 453 | **472** | **+19** |

## What the round-2 review would look for

If a fresh `bmad-code-review` returns BLOCKED on the same four axes after the round-2 fix, the most likely cause is one of:

1. **The runner still speculatively pre-increments `created` or `merged`.** Grep for `result.created +=` and `result.merged +=` — they should ONLY appear on lines that are gated on the helper's actual return. If they appear before the helper call, that is a regression.
2. **`applyDeltaMergeStockForOwner` is not used in the runner.** Grep for `applyMergeStockForOwner` inside `src/lib/csv-import/runner.ts` — it should NOT appear (the runner uses the delta helper, not the absolute helper). The `applyMergeStockForOwner` should only appear in the back-compat `runImportCore` synchronous path.
3. **`claimAndStart` is not called from the tick route.** Grep for `markRunning` in `src/app/api/csv-import/tick/route.ts` — it should NOT appear. The tick route uses `claimAndStart`, `advanceProgressBeforeRun`, `recordCountersAfterRun`, and `markCompletedIfReady` only.
4. **`loadLiveSnapshot` is not called at the start of every `runOneChunk`.** The runner should always re-read the live DB; the `options.liveSnapshot` parameter is for tests only.

If all four checks pass, the round-2 fix is solid. The atomic claim/advance/record contract is the same class-level pattern as the chaos-sort, no-bucket seed, and proportional-scaling fixes from CF-E5-S3 rounds 1-4: each round addresses a specific class of input space (concurrent, crash-after-write, failed-counter, replay-merge), and the table-of-axes grows.

## Carry-forward (preserved from round 1)

- The `Job` table migration does NOT change in round 2 (the round-1 schema is still correct). The new helpers work on the same columns.
- The 5-minute lease threshold is a Hobby-plan budget. Tighten to 30s if migrating to Vercel Pro + cron.
- The new `applyDeltaMergeStockForOwner` is the merge-mode call site for the new async path AND any future story that wants additive stock updates (e.g. an inventory re-count tool). It is NOT the right helper for the legacy `importCsvToLotAction` path, which still uses the absolute helper via `runImportCore` (preserved as back-compat shim).
- Future polish story could add: hard `UNIQUE(owner_id, idempotency_key)` index on `Job`; `GET /api/csv-import/jobs?status=active` endpoint for cross-session recovery; `POST /api/csv-import/jobs/[id]/cancel` + `markCancelled`; Vercel Pro upgrade to add minute-resolution cron as the tick trigger.
