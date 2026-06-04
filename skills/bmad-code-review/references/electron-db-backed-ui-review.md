# Electron DB-backed UI Code Review

Use this reference when an Electron story claims UI behavior backed by local database rows through main-process services, preload IPC, and a sandboxed renderer.

## Review pattern

1. Trace the data path end to end:
   - migration/table shape
   - repository read/write helpers
   - service wrapper
   - IPC handler registration
   - preload bridge exposure
   - renderer route/list/detail/action code
   - focused tests and runtime evidence
2. For psql-backed repository helpers, inspect both parser expectations and psql output arguments.
3. For renderer display, inspect row shape consistency across DB/preload/renderer.
4. For runtime evidence, require a real DB-backed row to render before accepting downstream UI actions.

## Durable psql delimiter pitfall

`psql --tuples-only` alone can still emit aligned, pipe-separated output such as:

```text
<uuid> | QA Pokémon Center UK qa-... | pokemon-center-uk
```

If the repository parser splits on tabs, `list*()` functions can silently return `[]` even though raw DB rows exist. This can leave the Electron UI in an empty state while inserts succeeded.

Preferred correction:

```text
--tuples-only --no-align --field-separator <tab>
```

Review expectations:
- All repository read paths that feed the same parser use the deterministic output args, not just one list function.
- Tests assert the executor args include `--no-align` and `--field-separator` set to tab for list/get read paths.
- Runtime evidence proves raw DB rows are visible through repository helpers and renderer UI.

Use BLOCKED when raw DB rows exist but app list/read helpers return zero rows for the acceptance path.

## Snake_case / camelCase renderer drift

DB/preload rows often use snake_case while renderer display code may expect camelCase (`vendor_module_key` vs `vendorModuleKey`, `worker_group_label` vs `workerGroupLabel`). Review for:
- visible `undefined` labels in runtime body text or screenshots
- default summaries rendered as `—` despite DB values existing
- actions using a missing ID/key because of shape drift

Verdict guidance:
- BLOCKED if shape drift breaks an acceptance criterion, action ID, child-list load, or required detail field.
- PASS WITH NOTES if the scoped flow works and drift only affects adjacent display polish; record a carry-forward cleanup.

## Evidence bundle to prefer

- Static validation: targeted repository tests, workspace typecheck/test/build, migration.
- Runtime smoke: Electron/Xvfb runner that seeds a QA DB row, verifies renderer row visibility, exercises create/list/detail/edit-validation, writes JSON + screenshot evidence, and cleans QA rows.
- Cleanup verification: confirm no `QA ...` rows remain after the run.
