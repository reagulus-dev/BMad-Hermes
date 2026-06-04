# Electron Renderer Canonical Registry Boundary

Use when an Electron static/sandboxed renderer must show data whose source of truth lives in a workspace package (for example a vendor registry, navigation contract, config copy, or feature catalog).

## Problem Pattern

A story requires the UI to render data from a canonical package, but the actual Electron app loads a static browser script (`index.html` -> `nav-init.js`) under `nodeIntegration: false`, `contextIsolation: true`, and `sandbox: true`.

A tempting shortcut is to paste a `const REGISTRY = [...]` mirror into the renderer. This compiles and may render, but it is not source-of-truth derived. It drifts as soon as the canonical package changes and should fail ACs that require registry-derived values.

## Preferred Fix Patterns

Choose one boundary and make it explicit:

1. **Main/preload IPC**
   - Main process imports the canonical package.
   - Preload exposes a narrow `window.<domain>.list()` API returning serializable metadata.
   - Renderer calls the bridge; no Node/DB/package imports in sandboxed renderer.
   - Best when data may later become dynamic or persistent.

2. **Generated JSON snapshot**
   - A build script imports the canonical package and writes a browser-safe JSON file under the renderer/build output.
   - Renderer fetches/imports the generated JSON.
   - Tests compare the generated snapshot to the canonical package.
   - Best for static registries with deterministic metadata.

3. **Browser-safe shared module**
   - Move only serializable constants/types into a package/file with no Node, Electron main, DB, Playwright, filesystem, or secret imports.
   - Both canonical consumers and renderer import that small safe module.
   - Best for small static contracts.

## Verification Checklist

- Renderer code does not contain a hand-maintained mirror of canonical data.
- A test proves renderer-visible data matches the canonical source or generated artifact.
- Future/placeholder entries have explicit status/disabled semantics and tests.
- Actual runtime path is checked: `BrowserWindow` -> `index.html` -> renderer script/route.
- If preload is involved, run an Electron/Xvfb smoke and inspect logs for preload module-resolution errors.

## Review Signals

Use BLOCKED when:
- The story says “derived from registry/source of truth” but the renderer hardcodes a copy.
- Future/placeholder item behavior is described but only the current happy-path item exists.
- Runtime smoke reaches the route but preload failures appear in logs and the story claims clean Electron runtime launch.
