# Helix psql deterministic read output pattern — 2026-05-17

## Trigger
Use this when a TypeScript/Electron story reads PostgreSQL rows through `psql` and parses stdout into typed rows.

## Failure signature
- Raw `psql` queries show rows exist.
- The repository helper, UI service, or runtime IPC path returns an empty list.
- The parser expects tab-separated fields, but the read command only uses `--tuples-only`.
- Default psql output remains aligned / pipe-separated, so `row.split('\t')` produces too few fields and every row is dropped.

## Durable fix
For read helpers that parse delimited stdout, request deterministic output explicitly:

```ts
const PSQL_TSV_OUTPUT_ARGS = ['--tuples-only', '--no-align', '--field-separator', '\t'] as const;
```

Use those args for list/get read paths before `--command`, for example:

```ts
[
  '--host', config.host,
  '--port', String(config.port),
  '--username', config.user,
  '--dbname', config.database,
  '--no-password',
  ...PSQL_TSV_OUTPUT_ARGS,
  '--command', sql,
]
```

Keep write paths focused on `--set ON_ERROR_STOP=1`; the deterministic-output requirement matters when stdout is parsed.

## Regression tests
Add tests that inspect the executor args for every stdout-parsing read path:
- list parent rows, e.g. `listTaskGroups()`.
- get parent row, e.g. `getTaskGroup()`.
- list child rows, e.g. `listTargetsByTaskGroup()`.
- get child row, e.g. `getTarget()`.

Required assertions:
```ts
expect(args).toContain('--no-align');
expect(args).toContain('--field-separator');
expect(args[args.indexOf('--field-separator') + 1]).toBe('\t');
```

Run a RED check before implementation: these tests should fail against plain `--tuples-only` calls.

## Runtime evidence pattern
After the fix, do not stop at unit tests. For DB-backed Electron CRUD, run an Electron/Xvfb smoke against the real preload + IPC path that proves:
- a real DB-backed parent row renders in the UI.
- child creation under that parent works.
- child list/detail views render from real DB rows.
- a validation guardrail still fires in the runtime path.
- any QA-created rows are cleaned up and cleanup is verified.

## Pitfalls
- Do not change the parser to split on `|` as the primary fix; aligned psql output includes padding and can corrupt field values.
- Do not treat raw DB rows existing as proof that the app read path works; prove the repository helper and runtime UI path can see them.
- Do not leave fixture rows behind after runtime evidence capture; clean up by stable QA naming prefix or returned IDs and verify zero remaining rows.
