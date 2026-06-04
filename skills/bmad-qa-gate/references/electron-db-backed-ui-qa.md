# Electron DB-backed UI Runtime QA Notes

Use this when an Electron/Xvfb QA gate must verify UI flows backed by a local database rather than mocked renderer state.

## Pattern

1. Run the app through the real Electron renderer/preload/IPC path under Xvfb.
2. Seed only minimal QA rows needed for the flow, using the same persistence layer or a direct DB helper.
3. Verify the UI renders those DB-backed rows before proceeding to downstream flow assertions.
4. If the UI shows an empty state, split diagnosis into three layers:
   - raw database query: does the row exist?
   - repository/helper function: does the app's list/read function return the row?
   - renderer/UI: does the row appear after navigation/reload?
5. Clean up QA rows after evidence capture.

## Durable pitfall: psql output parsing

Do not assume `psql --tuples-only` produces the delimiter a parser expects. In one Helix QA gate, raw `psql` showed rows like:

```text
<uuid> | QA Pokémon Center UK qa-... | pokemon-center-uk
```

but the repository parser expected tab-separated fields, so `listTaskGroups()` returned `[]` and the Electron UI stayed at `Task Groups — None configured` despite rows existing.

Preferred fixes to recommend during correction:

- make `psql` output deterministic with explicit no-align/field-separator options that match the parser, preferably `--tuples-only --no-align --field-separator <tab>`, or
- make the parser handle the actual output format intentionally, with regression tests.

After correction, the fresh QA gate should prove all three layers now agree:

1. Raw DB row exists.
2. Repository/list helper returns the row.
3. Renderer route shows the row and downstream child flow works.

For CLI-backed DB helpers, require regression tests that assert every read path feeding the parser includes deterministic output args, e.g. both list and get helpers for task groups and targets.

## Gate behavior

If raw DB rows exist but the app repository/list function returns zero rows, mark runtime QA `blocked`, not passed with notes. Downstream UI flows that depend on selecting that row remain unverified.

Record evidence for:

- runtime command and exit status
- UI empty/success state text
- raw DB query result shape, with secrets redacted
- repository/list helper result
- cleanup command/result, including a post-cleanup zero-remaining check for QA rows
- exact unverified downstream flow assertions

If the corrected runtime flow passes, explicitly mark the old blocked finding as superseded by later QA evidence rather than deleting the history. Keep any adjacent display polish issues separate from scoped-flow pass/fail: for example, snake_case/camelCase renderer display drift that only shows `undefined` labels in non-critical task-group metadata may be a carry-forward note, but shape drift that breaks required IDs, child-list loading, or detail fields is a blocker.
