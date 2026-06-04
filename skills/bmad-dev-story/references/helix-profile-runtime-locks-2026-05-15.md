# Helix Profile Runtime Locks — 2026-05-15

Reusable implementation pattern from HLX-2.4 for stories that protect browser profiles, worker sessions, or other runtime-owned local state with a distributed lock.

## Implementation shape

- Use a lock manager with:
  - namespaced lock keys, e.g. `lock:profile:{profile_id}`;
  - owner metadata and an unguessable token;
  - token-checked release;
  - conflict errors that expose current owner/status details;
  - a renewal operation that only extends the lease when the token still matches.
- For operator-visible stale recovery, prefer a persistent lock key with logical `expires_at` over Redis TTL-only expiry. TTL-only expiry makes stale locks disappear and prevents an operator from seeing/recovering them explicitly.
- Acquire the lock before launching the protected browser/profile/session context.
- If acquisition fails, do not launch.
- Keep the actual launched context/process in the owning service, not just a metadata handle.
- On normal close, close the actual runtime context first, then close local profile metadata/handle, then release the distributed lock.
- On renewal failure, stop renewal and close the runtime context/handle so local use stops before another owner can recover/acquire.
- On partial launch failure after the context exists but later metadata/inspection code fails, close the already-launched context and local handle before releasing the lock.
- Expose stale recovery in the operator UI as an explicit button/action only when the visible lock state is stale.

## Tests to add

- acquire succeeds and stores owner/token metadata;
- second active acquire fails with inspectable conflict details;
- renew succeeds for matching token and extends logical expiry;
- stale logical expiry remains visible via `inspect()`;
- token-checked release does not release another owner’s lock;
- explicit stale/operator recovery force-releases;
- service launch acquires lock before launching;
- service close closes context before lock release;
- renewal failure closes actual context and local handle;
- post-launch failure cleanup closes actual context before lock release;
- stale recovery button renders only for stale locks and invokes the recovery handler.

## Evidence wording

Keep evidence precise:

- Unit/service tests can verify protocol and lifecycle ordering.
- Component tests can verify explicit stale-recovery UI presence.
- Do not claim graphical click-through unless the actual Electron/browser UI was exercised.
