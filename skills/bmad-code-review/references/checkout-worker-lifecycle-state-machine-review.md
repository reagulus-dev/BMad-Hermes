# Checkout Worker Lifecycle State Machine Review Notes

Use when reviewing pure checkout-worker lifecycle/state-machine stories (for example HLX-5.2-style work) that define transitions, durable replay, rehydration, and worker event helpers without launching browsers or wiring live Redis/DB/Electron runtime.

## Durable replay / rehydration checks

- A durable transition record that includes both `previous_state` and `next_state` must validate both sides during replay.
- Do not accept replay code that only checks whether `next_state` is allowed from the internally tracked current state.
- Require `transition.previous_state === replayCurrentState` before applying `transition.next_state`.
- Add a focused regression test where the record's `previous_state` disagrees with replay current state but `next_state` would otherwise be valid; it must be rejected.
- Rehydration should reject corrupted/out-of-order history rather than silently normalizing it.

## Worker event envelope checks

- If the lifecycle context has `correlation_id`, `profile_id`, `task_id`, or `worker_id`, every event helper that can include those identifiers should thread them into the `HelixEvent` envelope/payload rather than hard-coding blanks.
- State-change, progress, and result event helpers should be reviewed together; do not pass state-change correctness while progress/result helpers drop available identifiers.
- Focused tests should assert representative envelope fields for all helper families, not only `event_type` and payload-local fields.

## Boundary stance

- Runtime QA is not required when the story is genuinely pure lifecycle logic with no DB writes, Redis publication, Electron UI, browser/profile launch, checkout automation, payment, CAPTCHA/OTP/3DS/SCA, or final-submit behavior.
- Use BLOCKED for durable replay correctness or required event-envelope identifier loss, because both affect future restart/audit/runtime integration trust even if current tests pass.
- Treat package-manager/Corepack wrapper failures as tooling notes when targeted package validation and a pinned/known-good workspace build path pass.