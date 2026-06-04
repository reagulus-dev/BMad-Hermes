# Client-polled background job review pitfalls

Use this reference when reviewing a web app story that moves long-running work (CSV imports, batch writes, bulk publishing, report generation) from one synchronous request/server action into a persisted `Job`/poll/tick model, especially when the "worker" is a client-polled API route rather than a real queue/cron worker.

## Review focus

A passing build/test suite is not enough. Review the job state machine against failure and retry boundaries:

1. **Atomic claim / lease**
   - A tick endpoint must atomically claim the next chunk before doing writes.
   - A plain `markRunning(jobId)` after a separate `getJob(jobId)` is not enough.
   - Look for a status/version/lease token guard such as `UPDATE ... WHERE id=? AND owner_id=? AND status IN (...) AND lease_expires_at < now() RETURNING *`, or an equivalent transaction/row lock.
   - The runner should use the claimed row/lease, not a stale pre-claim object.

2. **Progress and writes must share an idempotency story**
   - If card/order/listing writes happen before `processed_rows` is advanced, a crash after writes but before progress recording can reprocess the same chunk.
   - Either make per-row/chunk writes idempotent with durable operation keys, or advance progress only in a transactionally safe boundary that cannot falsely skip uncommitted work.
   - A stale-running resume sweep is useful for liveness but can cause duplicates if the chunk write is not idempotent.

3. **Do not count attempted writes as completed writes**
   - Counters like `created`, `merged`, `processed_rows`, and `completed` must reflect successful persistence.
   - Block when code increments `created += pendingCreates.length` before the create helper succeeds, catches the persistence error, and then advances `processed_rows` from attempted counts.
   - Failed chunks should either fail the job, retry without advancing progress, or record only actually successful rows.

4. **Retry merge semantics against current persisted state**
   - Merge-mode retries are unsafe if quantities/bucket sets are derived only from submit-time snapshots.
   - Reprocessing a chunk after a crash or concurrent tick can duplicate quantity, overwrite later progress, or regress stock.
   - Require tests that exercise retry/concurrent behavior for both create and merge modes.

5. **Client polling is not a single-threaded worker**
   - Browser timers, double-clicks, tab duplication, refreshes, and network retries can produce overlapping tick requests.
   - Treat `lastTickAt` freshness checks in the browser as UX hints, not as a correctness lock.
   - The server boundary must remain safe if two authenticated requests for the same owner/job arrive at the same time.

## Required focused tests for this class

Prefer tests that fail on the above failure modes:

- Two concurrent tick calls for the same job: only one claims and writes the chunk.
- Crash/write failure after domain writes but before progress: retry does not duplicate persisted rows.
- Create helper throws: `processed_rows` and `created_rows` do not advance falsely, or the job transitions to a clearly failed/retryable state.
- Merge retry: repeated processing of the same chunk is idempotent or explicitly blocked by claim/lease semantics.
- Terminal states are idempotent no-ops.
- Cross-owner job IDs return invisible/not-found semantics and cannot be ticked by another owner.

## Verdict guidance

Use **BLOCKED** when the story's purpose is reliability/resumability and the implementation cannot prove safe behavior under overlapping ticks or crash/retry boundaries, even if all static validation commands pass.

Use **PASS WITH NOTES** only when the server-side state machine is safe and remaining limitations are explicit product trade-offs, e.g. "Hobby plan jobs only progress while the browser is polling" or "live 10k-row verification remains post-deploy."