# Electron sandbox IPC boundary for DB-backed profile/service slices

Use this reference for Electron stories where a renderer-facing UI must reach Node-only persistence or local-service code (PostgreSQL via `psql`, filesystem profile handles, Playwright/Chromium profile lifecycle, etc.) while the BrowserWindow runs with `nodeIntegration: false`, `contextIsolation: true`, and `sandbox: true`.

## Pattern

1. Keep Node-only dependencies in the main process.
   - Example: `DbProfileStore`, `ProfileManager`, `node:child_process`, local `psql`, filesystem/profile handles.
   - Do not import these directly from sandboxed renderer components or static renderer scripts.
2. Add a main-process service wrapper.
   - Owns the DB-backed store and any non-serializable handles.
   - Exposes serializable methods such as `list`, `create`, `open`, `launch`, `close`.
   - Keep handles in a main-process map; return cloned/plain metadata objects to the renderer.
3. Register `ipcMain.handle(...)` channels in main before creating the window.
4. Add a preload bridge with `contextBridge.exposeInMainWorld(...)`.
   - Expose a small domain API like `window.helixProfiles` rather than raw `ipcRenderer`.
   - Keep channel names private to preload/main where practical.
5. Point `webPreferences.preload` at the built preload file while preserving sandbox settings.
6. Mount the actual runtime route that the Electron shell loads.
   - If `main.ts` loads `src/renderer/index.html` and that loads `nav-init.js`, validate that exact path, not only an isolated React/TSX screen.
7. Add tests at both boundaries.
   - Main-process service unit test with injected manager/store to prove handle ownership and validation.
   - Static renderer shell test importing the actual `nav-init.js`, navigating to the route, and asserting it calls the preload API and renders rows/errors.
8. Run service-path smoke after build when possible.
   - Create/list/open/close through the main-process service.
   - Verify the DB row directly.
   - Clean up the smoke row.

## Verification wording

- Passing isolated component tests is not proof that the Electron runtime route is mounted.
- Passing service smoke is not manual GUI QA.
- Headless/Xvfb launch failures or timeout shutdown quirks should be recorded as runtime-environment boundaries, not as durable negative claims about Electron.
- If the actual shell route is covered by a DOM test that imports the real renderer script, call it static shell runtime coverage, not full user interaction evidence.

## Common pitfalls

- Importing `@helix/db`/`DbProfileStore` directly into renderer code under `sandbox: true`.
- Wiring a React screen that compiles/tests but is not mounted by the actual `index.html`/renderer entry point.
- Returning non-serializable handles over IPC; keep them in main and return cloned metadata.
- Updating BMad status from `review_blocked` straight to complete after correction. Use `implemented_not_reviewed` and route to fresh code review.
