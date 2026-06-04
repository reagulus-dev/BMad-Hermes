# Redis Subscriber Consumer Pattern (2026-05-19)

Source: HLX-4.5 — Deliver Discord and desktop alerts for monitor events.

## Problem

A Redis bridge consumer was silently ignoring real monitor events due to:

1) Envelope mismatch:
   - Consumer expected top-level `event_name`.
   - Publisher (HLX-4.3) serialized a HelixEvent with top-level `event_type` and nested `payload`.
   - Result: real events silently dropped.

2) Redis subscriber output format mismatch:
   - Consumer spawned `redis-cli SUBSCRIBE monitor.events` (default mode).
   - Default redis-cli SUBSCRIBE output is numbered/quoted RESP-style lines, e.g.:
     - `3) "{...}"`
   - The parser only handled raw JSON lines starting with `{`.
   - Real Redis messages were silently ignored in the desktop process.

3) Tests did not prove the real subscriber path:
   - Prior tests:
     - Published via an in-process envelope instead of the Redis subscriber stdout.
     - Did not assert downstream service calls and persistence.
   - This hid the fact that real Redis events were not being consumed.

## Correct Pattern (generalizable)

For consumers that subscribe to events via a Redis subscriber child process:

1) Use `--raw` to get clean JSON payloads:
   - Spawn:
     - `redis-cli -h HOST -p PORT -n DB --raw SUBSCRIBE monitor.events`
   - With `--raw`, message payloads are emitted as raw JSON lines.
   - Metadata lines (subscribe/channel/count) can be ignored by shape.

2) Parser:
   - Primary: accept lines starting with `{` (raw JSON from `--raw`).
   - Defensive fallback: also parse numbered/quoted lines (e.g. `3) "{...}"`) in case `--raw` is accidentally dropped.

3) Envelope alignment:
   - Inspect the actual publisher’s serialized shape (e.g., HelixEvent):
     - `event_type` as canonical; `event_name` as fallback.
     - Use nested `payload` fields; maintain backward-compat fallbacks.
   - Map to the consumer’s internal envelope deterministically.

4) Process lifecycle:
   - The consumer instance must own the Redis subscriber child:
     - e.g. `this._redisSubscriber`.
   - `stop()` must kill that exact child (e.g., SIGTERM).
   - Avoid module-level singletons for the subscriber; they cause orphaned processes on restart.

5) Tests (must simulate the subscriber stdout path):
   - Mock `spawn` for `redis-cli SUBSCRIBE`.
   - Capture the child’s `stdout.on('data', handler)`.
   - Feed a production-shaped serialized event (e.g., from `serializeMonitorEvent()`) through that handler.
   - Assert:
     - Downstream service calls (e.g., `NotificationService.notify()`).
     - Persistence calls (e.g., `insertNotificationAttempt()`, `updateNotificationStatus()`).
     - Lifecycle: `stop()` kills the exact spawned Redis subscriber child.

## HLX-4.5 Specific Fixes

- notificationConsumer.ts:
  - Updated monitor.events handler to:
    - Treat `event_type` as canonical, `event_name` as fallback.
    - Use `payload` as event data, with backward-compat fallback.
    - Map to internal `MonitorEventEnvelope`.
  - Redis subscriber:
    - Now uses `redis-cli --raw SUBSCRIBE monitor.events`.
    - Added defensive parser fallback for non-raw numbered/quoted lines.
    - Instance tracks its own child; `stop()` kills that exact process.

- notificationConsumer.test.ts:
  - Added tests that:
    - Start consumer via `start()`.
    - Use the mock child’s `stdoutDataHandler` to inject:
      - A `serializeMonitorEvent()`-shaped HelixEvent.
    - Assert:
      - `NotificationService.notify()` with correct channel/event_name.
      - `insertNotificationAttempt()` and `updateNotificationStatus()`.
      - Stale-service regression: after settings change, consumer uses a new service instance.
      - `stop()` kills the Redis subscriber process.

## Lessons (generalizable)

- When a consumer subscribes to an event bus (Redis, etc.):
  - Never assume the event envelope; inspect the actual publisher.
  - A mismatch (event_name vs event_type + payload) can silently break all real events.
- Tests that “prove” consumer behavior must:
  - Start the consumer.
  - Use the real publisher shape.
  - Assert downstream service calls and persistence, not just “no error.”
- For child-process Redis subscribers:
  - Use `--raw` to avoid RESP-style output confusion.
  - Keep the handle on the consumer instance, not a module-level singleton.
  - Ensure `stop()` kills it to avoid orphaned subscribers across restarts.
