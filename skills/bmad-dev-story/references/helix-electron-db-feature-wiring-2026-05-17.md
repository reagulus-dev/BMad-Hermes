# Helix: Electron DB-backed feature wiring pattern — 2026-05-17

Used for HLX-3.4 (Targets) and similar features.

## Canonical wiring checklist

For a new DB-backed feature in Electron (e.g., targets, routes, workers):

- Migration:
  - Add migration SQL under @helix/db.
  - Validate via db:migrate on fresh DB.
  - Verify table/schema with psql.

- Repository:
  - Add repo module in @helix/db (e.g., targets.ts).
  - Use psql-based CRUD; match existing patterns.
  - Export from @helix/db index.

- Main process:
  - Add service that wraps DB calls (e.g., targetService.ts).
  - Add IPC handlers (e.g., targetIpc.ts) for channels.
  - Register handlers in main.ts at startup.

- Preload:
  - Expose safe IPC bridge via contextBridge (e.g., window.helixTargets).
  - Only expose serializable methods; no DB/Node leaks.

- Renderer:
  - Wire UI to preload bridge (e.g., nav-init.js).
  - No direct Node/DB imports.
  - Use existing patterns for list/detail/create/edit.

- Tests:
  - DB CRUD tests for repo.
  - Unit tests for guardrail helpers.
  - Renderer/UI tests where applicable.

- Validation:
  - pnpm -r run build
  - pnpm typecheck
  - pnpm -r run test
  - pnpm db:migrate

This is the baseline; future sessions should reuse this pattern.
