# Electron DB-backed Health Timestamp Runtime QA — Helix HLX-3.5

## Context

During an Electron/Xvfb QA gate for a DB-backed Routes screen, static validation and code review had already passed, but the real UI health-check path failed only at runtime:

```text
updateNetworkConfig failed: ERROR: invalid input syntax for type double precision: "2026-05-18T12:46:38.196Z"
... latency_ms = 150, last_failure_at = to_timestamp('2026-05-18T12:46:38.196Z')
```

## Root cause

The repository helper generated PostgreSQL `to_timestamp('<ISO string>')` for `last_failure_at` / `last_tested_at`.

In PostgreSQL, the active `to_timestamp(...)` overload expected a numeric epoch for this shape, so ISO-8601 strings failed at runtime even though TypeScript and unit coverage had passed.

## Correct fix

When the app already has ISO-8601 strings, emit timestamp updates as explicit timestamptz casts:

```sql
last_failure_at = '2026-05-18T12:46:38.196Z'::timestamptz,
last_tested_at = '2026-05-18T12:46:38.196Z'::timestamptz
```

Add regression coverage that inspects generated SQL and asserts:

- the ISO timestamp is cast as `::timestamptz`
- `to_timestamp(` is not emitted for ISO strings

## QA-gate behavior

If the QA gate finds a small in-scope runtime blocker:

1. Record the initial failing runtime evidence.
2. Apply a bounded same-story correction only if the root cause is clear and within the story scope.
3. Add or update a focused regression test.
4. Re-run the failed runtime QA path.
5. Re-run the broader validation commands needed for confidence.
6. Append both the initial blocker and the corrected pass to the story `## QA Findings` section.
7. Update `_bmad/state.json`, `_bmad/sprint-status.yaml`, and continuation docs to mark the old `runtime-unverified`/`QA pending` language as superseded.

Do not hide the first failure. The value of the QA gate is proving the real runtime path and capturing the correction trail.

## Evidence bundle pattern

A strong Electron/Xvfb DB-backed QA bundle includes:

- JSON result with explicit assertions and cleanup result
- screenshot path
- console/page error capture
- route/entity name and row ID used for the fixture
- confirmation that plaintext secrets did not render
- confirmation that QA-created rows were deleted after the run

Keep generated fixture names non-secret and redact or omit any real credentials.
