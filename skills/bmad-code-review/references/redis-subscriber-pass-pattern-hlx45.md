# Redis subscriber correction pass pattern — HLX-4.5

Use this as a concrete passing pattern after a review previously blocked a Redis Pub/Sub notification bridge for parsing the wrong `redis-cli SUBSCRIBE` output shape.

## Passing implementation shape

- Spawn Redis subscriber with raw output enabled:
  - `redis-cli --raw SUBSCRIBE monitor.events`
- Keep parser behavior aligned with that spawned command:
  - Primary path accepts raw JSON payload lines.
  - Non-payload metadata lines from `--raw` (`subscribe`, channel name, subscription count) are ignored.
  - Defensive fallback may tolerate default numbered/quoted output such as `3) "{...}"`, but the production command should still be explicit about `--raw` if the parser expects payload-only JSON.
- Transform the production publisher envelope, not a reviewer-invented shape:
  - HLX-4.3 publishes serialized `HelixEvent` JSON with top-level `event_type`, `occurred_at`, `task_id`, and nested `payload`.
  - The notification bridge maps that into the consumer’s notification/event envelope before delivery and persistence.

## Passing test shape

A trustworthy focused test should not call the in-process bus directly for the Redis case. It should:

1. Mock `node:child_process.spawn` and capture the spawned child object.
2. Capture the exact `stdout.on('data', handler)` registered by the production subscriber.
3. Assert the spawned args include `--raw`, `SUBSCRIBE`, and `monitor.events`.
4. Build the test payload using the production serializer, e.g. `serializeMonitorEvent(...)`, rather than handwritten JSON drift.
5. Feed raw-mode output through the captured stdout handler, including realistic metadata/noise lines plus the serialized JSON payload.
6. Assert downstream side effects, not just no-throw:
   - `NotificationService.notify(...)` receives expected event/product fields.
   - `insertNotificationAttempt(...)` receives expected `task_id`, `channel`, `status`, and redacted payload fields.
   - `updateNotificationStatus(...)` records the expected terminal status.
7. Assert lifecycle cleanup:
   - `stop()` kills the exact spawned Redis subscriber child with `SIGTERM`.

## Review verdict stance

Use `PASS WITH NOTES` when the production command/output mode and stdout parser test align and no blockers remain, but live Redis, desktop notification delivery, Discord receipt, visual QA, or founder-review readiness were not run. Explicitly preserve those as unverified areas rather than implying runtime QA.

Keep non-blocking hardening separate from the correction verdict, for example:
- legacy raw webhook values already present in local settings files may still need read-time sanitization;
- `INSERT` followed by `SELECT ... ORDER BY queued_at DESC LIMIT 1` is race-prone under concurrency and may need future DB hardening.
