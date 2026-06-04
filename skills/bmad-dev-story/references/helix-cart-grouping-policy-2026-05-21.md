# Pure Grouping Policy — HLX-5.5 Pattern (2026-05-21, updated 2026-05-22)

## What this is

Example of a pure domain-policy dev story: `cartGrouping.ts` — grouping policy for vendor stock events
inside one worker-owned cart/session. No runtime/UI/Redis wiring. Full unit-test coverage (94+ tests).

Canonical: `apps/orchestrator/src/cartGrouping.ts` + `cartGrouping.test.ts`.

## Key structural decisions

- Pure module: no Redis, DB, Electron, Playwright, or secret imports.
- Stateless `applyGroupingPolicy()` per invocation; does not track cart state across batches.
- Decision log is non-sensitive: only event IDs, reason codes, counts, item IDs.
- `GroupingReasonCode` union includes `'not_grouped'` for when ALL candidates are filtered.
- `knownWorkerIds` enforcement at policy entry (AC5), deferred to write/upsert boundary.

## correlation_id parsing for cross-worker detection

Format: `worker:<worker_id>:<task_id>`  
Parser extracts `worker_id` from index 1 of split on `:`.

## Test fixture contract

**`makeStockEvent(overrides)`**
- Spreads `overrides` into `event.payload` — not toplevel.
- Defaults: `event_id: 'evt-001'`, `correlation_id: 'worker:worker-a:task-001'`, `payload.price: 12.99`.
- To override price: `makeStockEvent({ price: 50.0 })` → `event.payload.price = 50.0`.

**`makeCandidate(overrides)`**
- Defaults: `per_item_max_price: 15.0`, `quantity: 1`, `vendor_module: 'coolshop-module'`, `priority: 1`.
- Spreads overrides into candidate object.

## Gate ordering (critical)

1. **Per-item max-price gate** (line ~240): `if (price > candidate.per_item_max_price) { continue; }`
2. **Max-cart spend gate** (line ~264): `if (max_cart_spend_hint !== null && estimated_total > max_cart_spend_hint) { return { status: 'not_grouped', reason_code: 'rejected_max_spend_exceeded' } }`

A candidate must pass gate 1 before gate 2 can be evaluated.

## `not_grouped` vs `grouped` with skipped count

- `status: 'not_grouped'` → ALL candidates filtered out.
- `status: 'grouped'` with `skipped_count > 0` → at least one valid candidate, some filtered.
- `status: 'grouped'` with `lines: []` → valid outcome (processed but empty group).

## Common test failure patterns

**Failure**: `result.lines[0]` is undefined, `status` is `'grouped'` but `lines` is empty.  
**Root cause**: Candidate's `price` exceeded `per_item_max_price` → filtered at per-item gate → no lines.  
**Fix**: Set `per_item_max_price` high enough for the price to pass the per-item gate before the test evaluates its intended gate.

**Failure**: Max-spend test gets `'grouped'` instead of `'not_grouped'`.  
**Root cause**: `per_item_max_price` default (15.0) < price (50.0) → per-item gate rejects before max-spend gate is reached.  
**Fix**: Set `per_item_max_price: 60.0` so candidate passes per-item gate and reaches max-spend gate.

**Failure**: Cross-worker/vendor test expects `'not_grouped'` but gets `'grouped'`.  
**Root cause**: Single invalid candidate → all filtered → `status: 'not_grouped'`. But if a second valid candidate exists, status becomes `'grouped'` with `skipped_count > 0`.  
**Fix**: Add a valid second candidate to force `status: 'grouped'`, then assert `skipped_event_ids` contains the rejected candidate.

## State update sequence

After dev-complete:
1. Commit implementation (cartGrouping.ts + cartGrouping.test.ts).
2. Update `_bmad/state.json`: `workflow_status: dev_complete`, `active_workflow: bmad-code-review`.
3. Update `_bmad/sprint-status.yaml`: `status: dev_complete`, `implemented_at`, `next_recommended_workflow: bmad-code-review for HLX-5.5`.
4. Update `CONTINUE-HERE.md`.
5. Commit artifact updates.
6. Route to `bmad-code-review`.

## HLX-5.5 review-blocked correction findings (2026-05-22)

After HLX-5.5 code review returned BLOCKED, these patterns were implemented to unblock:

### AC1: Typed candidate ownership fields

Do NOT use `any` casts or heuristic `correlation_id` parsing for cross-boundary enforcement.
Add typed fields directly to `GroupingCandidate`:

```typescript
interface GroupingCandidate {
  worker_id: string;       // required — not optional
  profile_id: string;      // required
  cart_session_id: string; // required
  task_group_id: string;
  target_id: string;
  priority: number;
  quantity: number;
  per_item_max_price: number;
  vendor_module: string;
  event: HelixEvent<MonitorStockFoundPayload>;
}
```

Enforce at the grouping loop boundary — compare typed fields directly, not via `correlation_id` parsing.

### AC5: applyGroupingPolicyForUpsert adapter pattern

When `knownWorkerIds` enforcement must be non-optional at production write/upsert paths:

```typescript
export function applyGroupingPolicyForUpsert(
  input: Omit<GroupingPolicyInput, 'knownWorkerIds'> & { knownWorkerIds: Set<string> }
): GroupingResult {
  if (input.knownWorkerIds.size === 0) {
    return makeEmptyResult(
      'rejected_unknown_worker',
      'knownWorkerIds must be non-empty for production grouping/upsert paths.'
    );
  }
  return applyGroupingPolicy({ ...input, knownWorkerIds: input.knownWorkerIds });
}
```

Tests: verify rejection when Set is empty; verify acceptance when Set is non-empty.

### AC6: Secret redaction for truncated secrets

Secret-like values can appear truncated in logs/persistence (e.g., `Bearer eyJhbG...sw5c`, `sk-abc...er-b`).
Redaction patterns must handle truncated forms:

```typescript
const REDACTED_TOKEN = '***';

function redact(value: string): string {
  return value
    .replace(/Bearer\s+\S+/gi, `Bearer ${REDACTED_TOKEN}`)        // Bearer JWT incl. truncated
    .replace(/\b(sk-[A-Za-z0-9]{5,})\b/gi, REDACTED_TOKEN)        // sk- keys ≥5 chars
    .replace(/\b(xoxb-[A-Za-z0-9-]{5,})\b/gi, REDACTED_TOKEN)   // xoxb- keys ≥5 chars
    // ... connection strings, session tokens, otp/sca markers, payment tokens, Discord webhooks
    ;
}
```

**Critical**: Use `{5,}` minimum length for sk-/xoxb- patterns. Truncated `sk-abc...er-b` has only 4 chars after `sk-`; a `{20,}` minimum would miss it.

**Test with both full and truncated forms**: inject `Bearer eyJhbG...sw5c` AND `sk-abc...er-b` into fields that are echoed in output (product_name, worker_id, correlation_id, messages). Assert raw values are absent from JSON-stringified output.

### Common test defect: worker_id collision with redact pattern

When testing redaction in skipped_reason messages, avoid `worker_id` values like `sk-abc123xyz` that match the sk- redact pattern. Use a value that triggers the `sk-` detection path but avoids word-boundary double-matching (e.g., `sk-abc...er-b` — 4 chars after `sk-` is below the `{5,}` threshold, and `-b` suffix acts as the boundary).

### Common test defect: CommonJS require in ESM test context

When a function like `applyGroupingPolicyForUpsert` must be imported from compiled TypeScript output in tests, do NOT use:

```typescript
// WRONG — CommonJS require fails at runtime with Jest+TypeScript transform
const { applyGroupingPolicyForUpsert } = require('./cartGrouping.js');
```

Use ESM top-level import:

```typescript
// CORRECT
import { applyGroupingPolicyForUpsert } from './cartGrouping.js';
```

### State JSON: avoid duplicate keys with successive patches

When updating `_bmad/state.json` across multiple patch calls in one session, successive patches can produce duplicate top-level keys. Fix: use `write_file` to rewrite the complete file cleanly after all changes.

## Related references

- `helix-pure-logic-no-runtime-dev-story-2026-05-20.md` — general pattern for pure logic + tests, no runtime wiring.
- `helix-known-worker-deferred-wiring-2026-05-21.md` — knownWorkerIds deferred enforcement pattern.
- `helix-jsonb-sql-quoting-2026-05-21.md` — JSONB SQL quoting and redaction patterns (for logging/persistence).