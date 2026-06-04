# Helix profile metadata persistence slice (2026-05-14)

## Context

Story class: monorepo desktop/service foundation story that persists previously in-memory profile/session metadata into local PostgreSQL while preserving an existing synchronous public API.

Concrete example: `HLX-2.3 — Persist profile metadata to PostgreSQL` in `/home/reagulus/projects/helix`.

## Durable lessons

- When a manager currently exposes synchronous methods (`create/open/close/list`) but persistence is moved to PostgreSQL, do not use fire-and-forget async writes unless the story explicitly accepts eventual consistency. Either convert the API to async with callers/tests updated, or provide a synchronous persistence boundary so reads after writes cannot race.
- Preserve existing in-memory object/reference behavior when introducing a store abstraction. Tests may depend on identity or mutation visibility even if persistence is now externalized.
- For pnpm/TypeScript monorepos, after adding a new imported workspace package, verify both TypeScript paths and package exports. App-level imports can require package `main`/`types` fields in addition to root `paths`.
- If a provider-specific delegate exits non-zero after writing files, treat its output as partial and untrusted: inspect disk, remove stray/generated source artifacts, patch bounded gaps, then rerun controller-owned validation.
- Evidence status should be `implemented_not_reviewed` after implementation/typecheck/test/build/smoke pass but before formal `bmad-code-review`.

## Validation pattern

Use the strongest available local-service validation:

```bash
pnpm services:health
pnpm db:migrate
pnpm -r run typecheck
pnpm -r run test
pnpm -r run build
```

Then add a direct service smoke for the new persistence boundary:

1. create a profile through the intended manager/store path
2. open it
3. close it
4. list profiles through the DB-backed store
5. query PostgreSQL directly for the persisted row
6. clean up the smoke fixture

## Reporting pattern

Record:

- delegate status separately from controller-verified status
- exact migrations/files touched
- exact validation commands and observed pass/fail
- whether direct DB persistence was proven
- next workflow as `bmad-code-review`, not founder/runtime completion
