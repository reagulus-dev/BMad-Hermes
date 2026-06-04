# Electron Renderer Generated Registry Snapshot Pattern

Use this when a sandboxed/static Electron renderer must display data owned by a canonical workspace package, but direct imports would cross Node/main-process boundaries.

## Trigger

- Electron renderer is static/browser-side (`index.html` + `nav-init.js` or similar).
- Renderer must show registry/config data from a workspace package such as `@helix/vendors`.
- Direct renderer imports from the canonical package are unsafe or impractical because the package may depend on Node/main-only modules or workspace resolution not available in the browser.
- A code review rejects a hand-copied renderer mirror as drift-prone.

## Pattern

1. Keep the canonical source in the workspace package.
   - Example: `@helix/vendors` exposes `listVendorModuleEntries()` and `getVendorModule()`.
2. Add a small generator under the consuming app, not in the renderer runtime.
   - Example: `apps/desktop-electron/scripts/generate-vendor-registry.mjs`.
3. The generator imports the built canonical package from `dist` and serializes only plain, renderer-safe data.
   - No functions, DB handles, Electron APIs, Playwright, child processes, or process-specific values in the generated artifact.
4. Emit a clearly marked generated browser module beside the static renderer.
   - Example: `apps/desktop-electron/src/renderer/vendor-registry.generated.js`.
   - Header should say generated, source of truth, and regeneration command.
5. Wire the app build so generation runs before TypeScript/Electron compilation.
   - Example: `build` runs `pnpm run generate:vendor-registry && rm -rf dist tsconfig.tsbuildinfo && tsc -p tsconfig.json`.
6. Renderer imports only the generated artifact.
   - Do not keep a hand-copied long-lived mirror in `nav-init.js`.
7. Tests should prove both behavior and source alignment.
   - Renderer route renders from generated data.
   - A canonical/generator test compares generated visible data to the workspace registry or generator output.
   - Future/placeholder registry entries get disabled/Coming-soon behavior and no runtime controls.

## Validation

Run:

```bash
PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH" pnpm typecheck
PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH" pnpm --filter <electron-app> test
PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH" pnpm build
```

When runtime evidence is requested, also run an Electron/Xvfb smoke and inspect output for preload/module-resolution failures.

## Review Signals

A reviewer should block if:

- Renderer still contains a full manual registry mirror.
- Generated data is not tied to the canonical package build.
- Future/placeholder modules are selectable as ready modules or expose runtime controls.
- The generated artifact includes Node/Electron/runtime handles.
- Build does not regenerate the snapshot, allowing drift.

## Status Wording

After a same-story correction using this pattern, use `implemented_not_reviewed` until fresh review passes. Do not mark the story complete just because typecheck/build pass.