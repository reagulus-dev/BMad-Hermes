# Redis CLI SUBSCRIBE output review note

Use this when reviewing a story that bridges Redis Pub/Sub messages into an Electron/main-process consumer, notification pipeline, dashboard, history writer, or worker orchestration path.

## Core pitfall

A subscriber can correctly parse the JSON payload shape but still fail production if it does not parse the **actual stdout format** emitted by the Redis client it spawns.

For `redis-cli SUBSCRIBE channel` without `--raw`, stdout is not guaranteed to be a payload-only JSON line. It can include Redis reply formatting such as subscribe metadata plus numbered/quoted payload lines, e.g. a payload may appear as something like:

```text
1) "message"
2) "monitor.events"
3) "{...json payload...}"
```

A parser that only handles lines where `trimmed.startsWith('{')` may silently ignore real published messages even if the JSON inside the payload has the correct `event_type` + `payload` shape.

## Review checks

1. Inspect the exact spawned command.
   - If it is default `redis-cli SUBSCRIBE ...`, require parsing of default Redis reply output.
   - If the implementation expects payload-only lines, require `redis-cli --raw SUBSCRIBE ...` or another documented raw-output mode.
2. Inspect tests for the subscriber boundary.
   - A test that directly publishes a pre-transformed in-process envelope only proves the bus-side path.
   - It does not prove the spawned Redis stdout parser.
3. Require a focused test that captures the spawned child `stdout.on('data', handler)` and feeds realistic stdout text.
   - Prefer using the production serializer (for example `serializeMonitorEvent()`) to build the JSON payload.
   - Feed the payload through the same stdout shape produced by the spawned command (`--raw` payload-only or default numbered/quoted reply output).
   - Assert downstream side effects such as `NotificationService.notify()`, `insertNotificationAttempt()`, and `updateNotificationStatus()`.
4. Also assert lifecycle cleanup for long-lived subscriber processes.
   - `stop()` / reset must kill the exact child process assigned during `start()`.

## Verdict guidance

Use `BLOCKED` when an explicit production event-driven AC depends on Redis Pub/Sub and the implementation only parses raw JSON lines while spawning default `redis-cli SUBSCRIBE`, or when tests bypass the stdout parser entirely. This leaves the event-driven production path unproven even if in-process bus tests pass.

Use `PASS WITH NOTES` only when the production command/output mode and tests align, but runtime/live Redis delivery remains separately unverified and truthfully scoped as not runtime QA.