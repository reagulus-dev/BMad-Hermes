# Electron IPC Handler Registration Review

Use this when reviewing Electron main-process IPC wiring, especially stories that add preload bridges or DB-backed renderer features.

## Key distinction

Electron has two different registration families:

- `ipcMain.handle(channel, handler)` for `ipcRenderer.invoke(...)`
- `ipcMain.on(channel, listener)` / event listeners for send/on flows

Cleanup APIs differ:

- `ipcMain.removeHandler(channel)` removes an invoke handler registered with `ipcMain.handle(...)`.
- `ipcMain.removeListener(channel, listener)` removes event listeners, not invoke handlers.

## Review rule

For modules that may be registered more than once in tests, hot reload, app re-init, or dependency injection:

1. If using `ipcMain.handle(...)`, require one of:
   - `ipcMain.removeHandler(channel)` before registering, or
   - a documented single-registration guard plus a test proving repeated registration behavior is safe.
2. If using `ipcMain.on(...)`, `removeListener` / `removeAllListeners` can be appropriate, but verify channel scope.
3. If the app only registers once at startup and there is no re-registration path in production/tests, do not block solely on `removeListener` misuse; record it as a carry-forward cleanup note.

## Blocking vs note guidance

Use `BLOCKED` when:

- tests or app lifecycle re-register `ipcMain.handle(...)` and the second registration can throw or bind stale services;
- handler duplication/staleness prevents an acceptance criterion from working;
- the implementation claims hot reload/test re-registration safety but only calls `removeListener` for invoke handlers.

Use `PASS WITH NOTES` when:

- startup registration is single-shot and verified enough for the story scope;
- the only issue is a future maintainability footgun around handler cleanup.

## Evidence to cite

- channel constants module imported by both preload and main;
- preload `ipcRenderer.invoke(...)` exposure;
- main-process `ipcMain.handle(...)` registration;
- any double-registration tests or explicit guards;
- whether runtime startup actually reaches the registration path.
