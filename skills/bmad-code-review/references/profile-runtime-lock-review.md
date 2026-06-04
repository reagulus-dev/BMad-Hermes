# Profile Runtime Lock Review Pattern

Use this reference when reviewing stories that prevent concurrent use of browser profiles, session directories, worker-owned resources, carts, or any local state that can be corrupted by two active owners.

## Core review question

Does the implementation prevent *actual runtime use* from overlapping, not merely metadata states from overlapping?

A lock implementation is incomplete if it releases, loses, or expires the lock while a browser/session/context can still be running against the protected profile directory.

## Checklist

- Lock acquisition happens before launching or opening the protected runtime resource.
- Failed acquisition prevents launch entirely.
- Conflicts return a clear error with inspectable owner/status details.
- Active locks are renewed or otherwise kept valid for the whole lifetime of the running context.
- Stale locks remain visible for explicit operator recovery. Avoid Redis TTL-only expiry for operator-facing stale recovery, because expired keys disappear and become indistinguishable from never-locked state.
- Stale recovery is exposed as an explicit operator action, not just a hidden IPC/API method.
- Normal close order is: close actual runtime context/process first, close local handle/metadata second, release distributed lock last.
- Failure-path cleanup after launch succeeds but later metadata/inspection code fails also closes the runtime context before releasing the lock.
- Renewal failure closes the actual runtime context/process and local handle before making the resource available again.
- Tests cover acquire, conflict, token-checked release, renewal, stale inspection, stale recovery action visibility, normal close close-before-release ordering, renewal-failure cleanup, and post-launch failure cleanup.

## BLOCKED signals

Use `BLOCKED` when:

- a browser/session/context returned by launch is ignored or not retained for close;
- normal close releases the lock before closing the real runtime context;
- lock TTL can expire while the runtime context continues using the protected profile;
- stale lock recovery exists only in backend/preload code with no explicit operator UI path;
- launch cleanup releases the lock after a partial launch without closing the already-launched context;
- tests only validate metadata handle state and do not prove the runtime context/process is closed.

## Evidence language

Be explicit about what was verified:

- `lock protocol verified` — acquire/conflict/release/renew/stale behavior is covered.
- `runtime lifecycle verified` — actual context/process close ordering is covered.
- `operator recovery verified` — visible stale state and explicit recovery action are covered.
- `GUI click-through not claimed` — component/service tests exist but no real graphical runtime evidence was gathered.
