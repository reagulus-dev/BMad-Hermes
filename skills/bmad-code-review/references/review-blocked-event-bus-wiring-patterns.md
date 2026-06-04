# Review-blocked event-bus wiring patterns

Use this reference when a story claims that events from an existing publisher/bus/stream are now bridged into a new consumer such as notifications, alerts, history, dashboards, or worker orchestration.

## Core lesson

A subscriber existing is not enough. Review must prove the subscriber understands the **actual payload shape emitted by the production publisher** and that tests exercise that same shape.

## Required checks

1. Identify the production publisher API and serialization helper.
   - Read the function that publishes to Redis/EventEmitter/DB/task events.
   - Read any serializer used immediately before publish.
   - Note exact top-level fields and nested payload fields.
2. Compare subscriber expectations to the publisher output.
   - Example mismatch: publisher emits `HelixEvent` with top-level `event_type` plus nested `payload`; subscriber only forwards messages with top-level `event_name`.
   - Treat a shape mismatch as a blocker when it prevents the claimed event-driven behavior.
3. Require tests using production-shaped fixtures.
   - Tests should use the real serializer or a literal payload copied from it.
   - Tests should fail if `event_type`/`event_name`, timestamp, task ID, or nested payload mapping drifts.
4. Verify the full consumer side effect.
   - Start the consumer, or invoke the exact transform boundary.
   - Assert the service method is called with expected formatted fields.
   - Assert persistence methods are called with expected channel/status/event payload.
   - If settings/toggles are mutable at runtime, assert a changed service/settings object affects the next event without restart.
5. Inspect lifecycle cleanup for long-lived subscribers.
   - A child process/EventEmitter subscription/socket handle created during `start()` must be the same handle stopped during `stop()`.
   - Watch for module-level vs instance-level handle drift, e.g. assigning `_redisSubscriber` while `_stopRedisSubscriber()` checks `this._redisSubscriber`.

## Blocker examples

- The only production callers emit `event_type`, but the new bridge filters on `event_name` and silently ignores real events.
- Tests mock database methods but never assert they were called.
- Tests publish directly to a helper with a simplified envelope that no production publisher emits.
- A singleton consumer is tested only for “does not throw” instead of delivery/persistence side effects.
- A stale service/settings fix is claimed but no regression test changes settings/toggles between two events.

## Non-blocking notes

- It is acceptable for live external delivery to remain deferred if the story truthfully claims attempted delivery plus persisted status, not successful receipt in the external channel.
- A mocked Redis/HTTP executor is fine for static review if the fixture matches the production serialized payload and side effects are asserted.
