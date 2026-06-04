# Helix Known-Worker Deferred-Wiring Pattern (HLX-5.4)

## Context

HLX-5.4 implemented worker-owned cart/session state with an ownership guard at `upsertWorkerCartSession()` in `packages/db/src/workerCartSessions.ts`.

The guard rejects unknown workers when a non-empty `knownWorkerIds: Set<string>` is supplied:

```typescript
if (knownWorkerIds.size > 0 && !knownWorkerIds.has(workerId)) {
  throw new WorkerCartSessionError('unknown_worker', sessionId, workerId);
}
```

## The Deferred-Wiring Design Question

The reviewer initially BLOCKED on the grounds that known-worker enforcement was "optional/unwired" — no production caller supplied `knownWorkerIds`, and no DB migration enforced worker existence via FK.

The controller's analysis: the enforcement logic is **already correct and durable** at the repository/write boundary. The "gap" is that no caller currently exercises it with a non-empty set, because the `checkout_workers` table does not yet exist to supply that set.

**This is a deferred-wiring design decision, not a missing implementation.**

## Resolution

Clarified the comment to document the design:

```typescript
// Enforce known-worker ownership if boundary set is provided.
// Future concrete worker configuration (from checkout worker config) MUST supply knownWorkerIds.
// Until a checkout_workers table exists, callers must pass knownWorkerIds so this check is active.
// If knownWorkerIds is provided but empty, treat as "not configured yet" — allow the call.
```

No logic change. Existing tests (107/107) continue to pass.

## Key Distinction

| Scenario | Correct Response |
|---|---|
| Guard logic is wrong/missing | BLOCK — fix the implementation |
| Guard logic is correct but comment is too thin | PASS WITH NOTES — clarify comment, document deferred-wiring |
| Guard logic is correct, caller doesn't yet supply the set (design: await config table) | PASS WITH NOTES — document as carry-forward deferred-wiring |

## Pattern for Future Epic 5 Stories

When evaluating "optional" enforcement at a repository boundary:

1. **Check if the guard already exists and is correct.** If it does, the question is whether it is *documented* and *reachable*, not whether it is *missing*.
2. **Distinguish optional-at-signature from missing-enforcement.** A function that accepts an optional parameter to activate enforcement is not the same as a function with no enforcement at all.
3. **Document deferred wiring explicitly.** Add a comment that names the future table/migration/config that will supply the required set, and the story/AC that will wire it.
4. **Issue PASS WITH NOTES with carry-forward**, not BLOCK, when the design is documented and the logic is correct.

## Related

- `references/helix-worker-owned-cart-session-state-2026-05-21.md` — broader HLX-5.4 pattern including IPC summary renderer, redacted references, and sensitive-value redaction.
