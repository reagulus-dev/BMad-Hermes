# Supabase service validation vs DB hardening boundary

Use this reference when reviewing BMad stories where a React Native/Expo service validates a domain invariant before writing to Supabase, but the database schema/RLS may still permit direct writes.

## Pattern observed

A story implemented availability block create/edit in the app service/UI:
- service loaded active/unarchived room units before insert/update
- service rejected date overlap with blocking bookings and other availability blocks
- browser QA verified the UI create/edit path
- live service smoke verified the service path

The smoke also attempted a direct insert against an archived room unit in the same establishment. Result: the DB accepted it because RLS/FKs proved establishment membership and same-establishment identity, but did not encode the `active=true AND archived_at IS NULL` product invariant.

## Review handling

This is not automatically a blocker when:
- the current product has only app-owned client paths,
- service/UI validation blocks the invalid path,
- evidence clearly records the DB boundary,
- future direct-write/API/admin surfaces are not being claimed safe.

Use `PASS WITH NOTES` rather than `PASS` when the story is otherwise verified but DB-level hardening remains deferred.

Escalate to `BLOCKED` when:
- direct writes are an intended supported surface,
- external APIs/admin tools can bypass the service,
- the invariant protects tenant isolation or money/security-critical data,
- the story claims DB-level enforcement or release readiness without evidence.

## Evidence to request or run

For Supabase-backed stories, prefer a live smoke that records both:
1. app/service path succeeds for valid data and rejects invalid data;
2. direct DB write attempt outcome for the same invariant.

Record the exact boundary in the story artifact, for example:

- `service_validation_archived_room_rejected: true`
- `direct_archived_room_block_db_rejected: false`
- note: `UI/service validation protects current app path; DB trigger/RPC hardening deferred.`

## Common future hardening options

- Move writes behind a transactional RPC that performs invariant checks.
- Add `BEFORE INSERT OR UPDATE` triggers to validate referenced row status.
- Add exclusion constraints/triggers for cross-table overlap races where Postgres constraints cannot directly express the invariant.
- Re-run live Supabase smoke after migration, not just TypeScript tests.
