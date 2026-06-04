# Review-Blocked Correction: Event Bus Wiring Patterns

## Context

When a review BLOCKS a story because an in-process event bus has no production caller, the default instinct is to find who *should* call `publishXxx()` and wire it. Sometimes that is correct. Often the real architecture is: external event sources publish to a shared transport (Redis Pub/Sub, NATS, a message queue), and the consumer should *subscribe* to that transport and re-emit onto the internal bus.

This reference documents both patterns.

---

## Pattern A — Caller Wiring (direct invoke)

**When to use:** The event source already knows about the bus and the gap is purely "no one called it yet."

The event source is co-located or has a direct import path to the consumer module.

```
External Source (MonitorScheduler)
  → calls publishMonitorEventToNotificationBus() directly
  → NotificationConsumer handles it
```

**Correction procedure:**
1. Identify the event source (MonitorScheduler, WorkerLifecycle, task-event service).
2. Import and call `publishMonitorEventToNotificationBus(envelope)` at the right emission point.
3. Add test that fires the event and asserts `service.notify()` was called.
4. Validate.

---

## Pattern B — Transport Bridge (subscribe + re-emit)

**When to use:** The event source publishes to an external transport (Redis, NATS, SQS) that the consumer can subscribe to. The in-process bus is a convenience layer on top of that subscription.

```
External Publisher (MonitorScheduler/WorkerLifecycle)
  → redis-cli PUBLISH monitor.events <json>
  → NotificationConsumer._startRedisSubscriber()
      spawns redis-cli SUBSCRIBE monitor.events
      parses stdout line-by-line
      re-emits MonitorEventEnvelope on internal notificationBus
  → NotificationConsumer._handleEvent()
      calls getNotificationService() fresh
      calls service.notify()
      persists via insertNotificationAttempt / updateNotificationStatus
```

**Key architectural properties:**
- Publisher is unmodified — it already publishes to Redis; it does not need to know about the notification bus.
- Consumer subscribes to the same Redis channel it already publishes to.
- The internal bus (EventEmitter) remains useful for: direct test injection, desktop-notificationIPC calls, and any other in-process producer.
- `startNotificationConsumer()` takes **no service argument** — it calls `getNotificationService()` fresh inside `_handleEvent()` so Settings saves propagate without restart.
- Redis subscriber is a lifecycle-managed child process (`_redisSubscriber: ChildProcess | null`).
- Graceful degradation if `redis-cli` is unavailable — log warning and continue with in-process path only.

**Correction procedure (Pattern B):**
1. Confirm the external transport channel name (e.g., `monitor.events` from `EVENT_CHANNEL.MONITOR_EVENTS`).
2. Confirm how the external publisher encodes messages (e.g., `redis-cli PUBLISH monitor.events <json>` where json is `JSON.stringify({ type, payload, timestamp })`).
3. Add a subscriber启动 function to the consumer:
   ```ts
   private _startRedisSubscriber(): void {
     const { host, port, db } = parseDbConfig(); // or get from env
     this._redisSubscriber = spawn('redis-cli', [
       '-h', host, '-p', String(port), '-n', String(db),
       'SUBSCRIBE', 'monitor.events'
     ]);
     this._redisSubscriber.stdout?.on('data', (chunk: Buffer) => {
       // parse line-by-line: Redis protocol is multi-line
       // messages come as: message <channel> <payload>
       const lines = chunk.toString().split('\n');
       for (const line of lines) {
         try { /* parse JSON from payload field */ } catch { /* ignore non-JSON */ }
       }
     });
     this._redisSubscriber.on('error', (err) => {
       console.warn('[NotificationConsumer] redis-cli error:', err.message);
     });
   }
   ```
4. Call `_startRedisSubscriber()` after `notificationBus` is listening.
5. Clean up in `_stopNotificationConsumer()` or equivalent: `this._redisSubscriber?.kill()`.
6. Add tests that mock the DB persistence layer (`vi.mock('@helix/db')`) and assert `insertNotificationAttempt`/`updateNotificationStatus` are called with correct envelope data.
7. Validate: targeted tests + typecheck + build.

---

## Which Pattern to Pick

| Signal | Pattern |
|--------|---------|
| Event source imports the bus/module directly | A — caller wiring |
| Event source publishes to shared transport (Redis, NATS, SQS) | B — transport bridge |
| Multiple external sources publish to same channel | B — one subscriber, multiple re-emits |
| You need to modify the event source to add bus calls | A might mean redesign — consider B instead |
| Test injection needs to fire events without Redis | Use in-process `publishMonitorEventToNotificationBus()` directly in tests |

---

## Stale Service After Settings Save (Companion Fix)

When `NotificationConsumer` is constructed with a `NotificationService` instance and `saveSettings` replaces that service in `notificationIpc.ts`, the consumer still holds the old reference.

**Fix:** Do not hold `_service` as a field. `startNotificationConsumer()` takes no service argument. Inside `_handleEvent()` (or equivalent):

```ts
private _handleEvent(envelope: MonitorEventEnvelope): void {
  const service = getNotificationService(); // fresh lookup every event
  service.notify(envelope).then(/* persist */);
}
```

This way, when `saveSettings` IPC does:
```ts
_notificationService = new NotificationService(newSettings);
```
...the next event automatically reads the new service. No restart required.

---

## Persistence Test Pattern

When the notification consumer calls DB helpers (`insertNotificationAttempt`, `updateNotificationStatus`), test with `vi.mock`:

```ts
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { insertNotificationAttempt, updateNotificationStatus } from '@helix/db';

vi.mock('@helix/db', () => ({
  insertNotificationAttempt: vi.fn().mockResolvedValue(undefined),
  updateNotificationStatus: vi.fn().mockResolvedValue(undefined),
}));

describe('notificationConsumer event → persist', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('calls insertNotificationAttempt and updateNotificationStatus on success', async () => {
    // fire publishMonitorEventToNotificationBus(envelope)
    // await short tick
    expect(insertNotificationAttempt).toHaveBeenCalledWith(
      expect.objectContaining({ eventType: envelope.type, /* ... */ })
    );
    expect(updateNotificationStatus).toHaveBeenCalledWith(
      expect.objectContaining({ status: 'delivered' })
    );
  });
});
```

Key points:
- `vi.mock` is hoisted — use `vi.hoisted()` for shared mock data structures referenced at hoist time.
- Call `vi.clearAllMocks()` in `beforeEach`.
- Await a short tick (`await new Promise(r => setTimeout(r, 10))`) after firing the event to let async handlers complete.
- Assert on the shape of the call argument, not just `toHaveBeenCalled`.

---

## Validation Checklist After Correction

- [ ] Targeted tests pass: `notificationConsumer`, `notifications`, `db`
- [ ] `tsc --noEmit` clean on the affected packages
- [ ] `git diff --check` clean
- [ ] Story artifact updated: status → `implemented_not_reviewed`, correction section appended
- [ ] `_bmad/state.json` updated: `workflow_status`, `blockers` cleared, `next_recommended_workflows` set to fresh `bmad-code-review`
- [ ] `_bmad/sprint-status.yaml` updated: story status → `implemented_not_reviewed`, `review_verdict: PENDING`
- [ ] `CONTINUE-HERE.md` updated if present