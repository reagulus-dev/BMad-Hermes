# Electron Runtime Boundary Review Notes

Use this reference when reviewing Electron stories that claim UI/runtime wiring, local service access, database persistence, profile/session management, or Node-backed operations from a screen/component.

## Core lesson

A component importing the right service is not enough evidence that the running Electron app uses it. Review must trace the actual runtime path from `BrowserWindow` loading through HTML/bundle/preload/router to the claimed screen or IPC handler.

## Review checklist

1. Trace the real app entrypoint:
   - `main.ts` / main process `BrowserWindow` creation.
   - `loadFile`, `loadURL`, dev-server URL, or bundled renderer output.
   - `index.html` scripts and the renderer bootstrap.
   - Router/nav mapping from the target route to the target component.

2. Verify renderer/preload security boundaries before accepting service access:
   - `nodeIntegration`
   - `contextIsolation`
   - `sandbox`
   - preload script presence and exposed API shape
   - IPC handlers registered in main process
   - built preload output format and actual runtime load logs
   - preload runtime import graph: safe constants/types only, not main-process service modules

3. For ESM Electron apps, inspect the built preload artifact, not just TypeScript source:
   - `package.json` with `"type": "module"` plus plain `dist/preload.js` can leave ESM `import` statements in preload output.
   - Electron may reject that preload at runtime with `SyntaxError: Cannot use import statement outside a module` even when TypeScript, tests, and build pass.
   - A preload load failure means `window.<bridge>` is absent; renderer tests with a mocked bridge do not prove the real app works.
   - Prefer a CJS `.cjs` preload, a dedicated preload build config, or another explicitly verified Electron-compatible preload packaging path.

4. Treat these as blockers when the story claims runtime UI behavior:
   - The actual shell loads a static placeholder script while the reviewed TSX/React screen is never mounted.
   - A sandboxed renderer imports a Node-only service (`node:child_process`, filesystem, psql, Redis CLI, Playwright, secrets, local DB clients) directly.
   - A renderer screen hardcodes a hand-maintained copy of canonical package/registry/config data when the story requires source-of-truth-derived values. Require IPC, a generated browser-safe snapshot, or a browser-safe shared module plus parity tests.
   - Future/placeholder registry items are claimed but no disabled/coming-soon behavior exists beyond the current happy-path item.
   - Preload imports a module that also imports `ipcMain`, `ProfileService`/service classes, DB packages, Playwright, psql, Redis, or other main-only runtime code.
   - The compiled preload fails to load during an actual Electron smoke, so the bridge is unavailable.
   - Tests import/render the component in isolation but no test or runtime path proves the component is reachable from the running shell.

5. Prefer the safe architecture for Node-backed features:
   - Main process owns Node/local-service access.
   - Shared IPC channel constants live in a preload-safe module with no main/service imports.
   - Preload exposes a narrow typed API via `contextBridge` and imports only Electron preload APIs plus safe constants/types.
   - Renderer calls the preload API, not `@helix/db`, `child_process`, raw filesystem, or CLI helpers directly.
   - Tests cover IPC handler behavior, preload API consumption, renderer API consumption, and at least one runtime smoke proving preload loads.

## Evidence wording

Use precise language:

- `component-level validation passed` when TSX compiles/tests but is not mounted in runtime.
- `service-path validation passed` when a Node/service smoke proves DB or filesystem behavior outside the UI.
- `preload-loaded runtime bridge verified` only when an actual Electron launch shows the preload loaded and the expected `window.<bridge>` exists.
- `runtime-shell wiring verified` only when the actual Electron entrypoint routes to the component/API under the current security settings.

## Common verdict

Use `BLOCKED` when the story acceptance criteria require operator-facing Electron runtime behavior and review finds only service/component validation without actual shell wiring, finds a direct Node import that cannot work under the configured renderer sandbox, finds a preload import graph that pulls in main-process service/DB code, or verifies that the compiled preload fails to load in the actual Electron runtime.
