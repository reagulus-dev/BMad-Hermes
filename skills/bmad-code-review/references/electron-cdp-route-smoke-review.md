# Electron CDP Route Smoke for Code Review

Use this when a BMad code review needs evidence that the *actual Electron shell route* renders the target screen, not just that component/unit tests pass.

## When to use

- The story claims operator-facing Electron UI behavior.
- A previous review found that the real shell still showed a static placeholder.
- Acceptance criteria require renderer data to come from a generated/browser-safe boundary.
- Xvfb smoke proves the app starts, but does not assert the route content.

## Evidence target

Capture assertions from the real `BrowserWindow` load path:
- `BrowserWindow.loadFile/loadURL` target is the expected shell.
- Runtime navigation function/router is available.
- Navigate to the target route through the real shell path.
- Assert screen root `data-testid` is present.
- Assert a representative row/detail/copy is visible.
- Assert old placeholder content is absent.
- Record whether console/preload errors appeared.

## Tooling pattern

Prefer tracked background processes over shell-level backgrounding:
- Do **not** use `cmd &` inside a foreground `terminal` call; Hermes rejects this and it also makes cleanup brittle.
- Start Electron with `terminal(background=true)` or a wrapper script that owns and terminates the child process in `finally`.
- Poll `http://127.0.0.1:<port>/json` until DevTools Protocol exposes a page target.
- Use CDP `Runtime.evaluate` to invoke route navigation and query DOM state.
- Kill the Electron process after collecting evidence.

## Dependency hygiene

Do not install new WebSocket/CDP packages during review unless the project already uses them or the user authorizes dependency changes. If Python `websocket`/Node `ws` are unavailable, options are:
- Use a small stdlib-only WebSocket CDP probe in `/tmp` as a review helper.
- Query an already-running reviewed Electron process via CDP if one is available and clearly from the target repo/port.
- Fall back to Xvfb smoke only, but record it as weaker evidence and avoid claiming route-level runtime verification.

## Example assertions

For a Vendor Modules route, suitable CDP evidence is:

```json
{
  "hasVendorModulesPage": true,
  "hasPokemonCenterRow": true,
  "hasPlaceholderHeadline": false,
  "includesPokemonCenterUk": true,
  "includesCadence": true,
  "includesConfigured": true
}
```

## Verdict handling

- `PASS`/`PASS WITH NOTES`: route root and representative content render through the actual shell path; startup smoke has no relevant preload/module-resolution errors.
- `PASS WITH NOTES`: CDP/Xvfb verifies shell wiring but human visual QA/founder review is still unclaimed.
- `BLOCKED`: the real shell still renders a placeholder, route navigation is unavailable, the preload fails to load, or route content only passes in isolated component tests.
