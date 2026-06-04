# Next.js / Prisma sales-inventory review checklist

Use for CardForge-style stories where recording sales mutates inventory availability and displays sale profit.

## Review checks

- Treat sale + inventory consistency as a correctness boundary, not UI polish.
- Inspect create/update/delete service code for atomicity:
  - Sale row creation/update/delete and card quantity/status updates should be in one Prisma transaction or an equivalently tested atomic boundary.
  - A mid-sequence failure must not leave a sale persisted without inventory adjustment, inventory restored before a rejected update, or inventory restored before a failed delete.
- Inspect update math, not just create/delete:
  - Same-card sale quantity edits must restore the prior quantity before validating/applying the new quantity, and must subtract from the restored/current value rather than a stale pre-restore value.
  - Same-card edits for a sale that consumed the last unit must validate against effective availability (`current card quantity + existing sale quantity`) before rejecting `SOLD` / zero-quantity state; otherwise a legitimate sold-out linked sale can become uneditable.
  - Re-linking from card A to card B must restore A and subtract B correctly.
  - Explicit unlink (`cardItemId: null`) must restore the previous card quantity and status; do not allow null/undefined coalescing to treat explicit null as “keep existing card” for inventory logic.
  - Explicit unlink must preserve every other submitted sale edit field. A special unlink branch that only writes `{ cardItemId: null }` silently drops price/fees/status/date/notes/quantity changes from the same form submit.
  - Status transitions must drive inventory semantics. If the UI exposes `PENDING`, `COMPLETED`, `CANCELLED`, or `REFUNDED`, creation and status-only updates must define which statuses consume inventory and must restore/deduct stock when moving between consuming and non-consuming statuses.
  - Rejected updates must not leave partial inventory side effects.
- Require focused tests for update-path behavior:
  - same-card quantity increase/decrease
  - same-card edits when the linked card is currently `SOLD`/quantity zero because the existing sale consumed the last unit
  - card re-link
  - card unlink, including unlink combined with other sale field edits
  - status transitions between consuming and non-consuming sale states
  - insufficient quantity rejection with no side effects
  - transaction/atomicity failure cases when the implementation supports mocking them
- Review UI field parity:
  - If the story says sales capture/display platform, sale date, sold price, fees, shipping charged, shipping cost, quantity, status, linked card, notes, and profit/net contribution, verify both form capture and ledger display. Showing only shipping cost is not enough when shipping charged is named.
- Review client refresh after server actions:
  - If a client component copies server-provided rows into local state, create/update actions must update local state from returned action data, force a remount, or synchronize local state from refreshed props. Calling `router.refresh()` alone may not update a ledger that renders from stale `useState(initialRows)`.
  - Delete-only local updates do not prove create/update reachability.

## Verdict guidance

Use `BLOCKED` when any of these break an explicit AC:
- inventory update math can write the wrong quantity/status
- explicit unlink/relink desynchronizes inventory
- sale and inventory writes can be left partially applied without a transaction/equivalent guard
- required displayed sale fields are missing from the ledger
- create/update succeeds but the visible ledger remains stale
- update-path inventory tests are absent while update is implemented

Passing validation commands do not override these product correctness blockers; record validation as passing but verdict as `BLOCKED`.
