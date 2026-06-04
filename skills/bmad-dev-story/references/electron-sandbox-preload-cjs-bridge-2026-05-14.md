# Electron sandbox preload CJS bridge correction

Use this reference when a BMad Electron story wires a sandboxed renderer (`nodeIntegration: false`, `contextIsolation: true`, `sandbox: true`) through preload IPC and runtime smoke must prove the bridge actually loads.

## Durable pattern

1. Treat Electron preload as a runtime artifact, not just TypeScript output.
   - If the app package is ESM (`"type": "module"`) and `tsc` emits `dist/preload.js` containing ESM `import` statements, Electron sandbox preload can fail with `Unable to load preload script` / `Cannot use import statement outside a module`.
   - Prefer a `.cts` preload source when using plain `tsc`, so the build emits `dist/preload.cjs`.
   - Point `BrowserWindow.webPreferences.preload` at the built `.cjs` file.
2. Clean build output before compiling after preload format changes.
   - Stale `dist/preload.js` can remain and make reviews/smokes ambiguous.
   - A package build script such as `rm -rf dist tsconfig.tsbuildinfo && tsc -p tsconfig.json` is acceptable for this class of local Electron app.
3. Keep the sandbox preload runtime import graph narrow.
   - Runtime imports should be Electron preload APIs (`contextBridge`, `ipcRenderer`) and only truly preload-safe constants/types.
   - Do not import main-process IPC registration modules, services, DB packages, Playwright/profile managers, or `psql` boundaries into preload.
   - Under Electron sandbox preload, avoid local relative `require(...)` chains unless you have explicitly verified they work in that runtime. A self-contained preload with duplicated serializable channel strings can be safer than sharing constants via a local runtime import.
4. Keep main-process IPC constants separate from main services.
   - Put channel constants in a small dependency-free module for `ipcMain` registration.
   - If preload cannot safely import that module at runtime, duplicate only the serializable strings in preload and add a test that both sets match / that preload contains no forbidden imports.
5. Validate the actual Electron entry path.
   - Static component tests are not enough. Launch the actual app with Xvfb when headless, attach via CDP, and evaluate `window.<bridgeName>` on the page loaded by `BrowserWindow`.
   - Treat a smoke that proves bridge exposure as runtime preload evidence, not full manual GUI interaction.

## Example smoke shape

- Launch Electron with `xvfb-run` and `--remote-debugging-port=<port>`.
- Attach with Playwright `chromium.connectOverCDP`.
- Find the `index.html` page.
- Evaluate:

```js
({
  hasBridge: typeof window.helixProfiles === 'object' && window.helixProfiles !== null,
  methods: window.helixProfiles ? Object.keys(window.helixProfiles).sort() : [],
  pageUrl: window.location.href,
})
```

Expected evidence for a profile bridge:

```json
{"ok":true,"hasHelixProfiles":true,"helixProfileMethods":["close","create","launch","list","open"],"pageUrl":"file:///.../index.html"}
```

## Verification wording

- `PASS`: preload loads and exposes the bridge in the actual Electron runtime route.
- `Not claimed`: manual button-level GUI QA, unless the smoke actually exercises the buttons and verifies resulting UI/service state.
- If the app is not a git repository, record that git diff/status evidence is unavailable rather than omitting the source-control boundary.

## Pitfalls

- Do not assume `tsc` output format is suitable for Electron preload just because TypeScript compiles.
- Do not leave stale preload outputs in `dist`; reviewers may inspect the wrong artifact.
- Do not import `profileIpc.ts` from preload when that module imports `ipcMain` or service/DB code.
- Do not count `electron --version` as proof that the preload script loads.
- If an early smoke logs `module not found` for a preload-local dependency, capture the fix as narrowing/self-containing the preload runtime graph, not as a durable negative claim about Electron or browser tooling.
