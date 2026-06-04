# Electron Notification / Alert Story Review Notes

Use this reference when a BMad story claims desktop notifications, Discord/webhook alerts, alert history, notification settings, or event-driven delivery from monitor/task events.

## Core review stance

A notification package plus Settings/History UI is not enough. If acceptance criteria say a monitor/task event creates an alert, review must find the concrete production event-consumer path that invokes delivery and persistence.

## Required trace

Trace the full path, not just unit-tested helpers:

1. Event source
   - Redis/task-event/monitor-event surface that emits or lists the relevant event types.
   - Event names match the story acceptance criteria (`stock_found`, `worker_started`, etc.).
2. Event consumer / transform boundary
   - A production module subscribes, polls, or otherwise receives typed events.
   - It transforms the event payload into notification formatting input.
   - It applies event toggles before delivery.
3. Delivery
   - Desktop delivery is wired to a real main-process-safe executor (for Electron, usually `new Notification(...)`) or is explicitly mocked and not claimed as runtime delivery.
   - Discord/webhook delivery either resolves an opaque secret reference through a safe secrets boundary or explicitly remains mocked with truthful UI/operator copy.
4. Persistence
   - Delivery attempts are inserted before/around delivery and status/failure is updated after delivery.
   - Alerts history reads from those persisted attempts, not only from manually seeded/test rows.
5. Redaction boundary
   - Raw webhook URLs are rejected or converted before save/test/persistence/logging boundaries.
   - Renderer-visible settings and history never return a raw URL.

## Blockers

Use BLOCKED when any explicit event-driven alert AC is present and:

- No production path invokes `NotificationService.notify(...)` (or equivalent) from monitor/task events.
- No path persists event-driven attempts/statuses into notification history.
- Settings can persist and re-expose a raw webhook URL through renderer -> IPC -> main persistence.
- UI copy says a Discord channel should receive a test message while the handler only uses a mock executor.
- Desktop notification support exists only as an injectable unit-test contract and is not wired in Electron main/runtime code while runtime delivery is claimed.

## Non-blocking notes to consider

- Bound/coerce IPC-provided history limits before interpolating into SQL or CLI commands.
- Prefer `INSERT ... RETURNING id` over `INSERT` followed by `SELECT ... ORDER BY queued_at DESC LIMIT 1`, which is race-prone under concurrent inserts.
- Distinguish static tests/typechecks from runtime alert delivery; passing package and renderer tests do not prove event-driven notification delivery.
