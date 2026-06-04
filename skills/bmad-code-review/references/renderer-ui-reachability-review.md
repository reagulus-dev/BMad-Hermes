# Renderer UI Reachability Review

Use this reference when an Electron/browser story claims operator-facing UI behavior, especially CRUD flows under a static renderer shell.

## Why this matters

A story can pass typecheck, build, migration, repository tests, and IPC boundary review while still failing its acceptance criteria because the UI path is unreachable or broken at runtime. Review must verify that the user can actually reach the claimed action from the rendered route.

## Focus checks

1. Rendered action exists
   - Verify buttons/links/forms are actually appended to the DOM.
   - Watch helper APIs such as `createElement(tag, options, children)` where callers accidentally pass `options.children` that the helper ignores.

2. Selected entity shape is correct
   - Trace list-row click state into detail renderers.
   - Confirm detail components receive the full selected object when they dereference object fields, not just an ID string.
   - Look for undefined labels, undefined IDs in test IDs, or action handlers called with `undefined`.

3. Success paths call existing refresh functions
   - Search create/edit/delete success paths for undefined refresh or navigation helpers.
   - A successful mutation that throws during refresh still fails the operator flow.

4. Edit/delete paths are reachable
   - Do not count an `editThing()` function as satisfying edit criteria unless a rendered row/button/menu calls it.
   - Static text rows are not an edit UI.

5. Tests cover the route, not just modules
   - Require focused renderer/JSDOM or browser tests for add/list/edit flows when the story acceptance criteria are UI-facing.
   - Existing broad shell tests may pass while the new route action remains unreachable.

## Minimal probe pattern

For a static renderer shell, a reviewer can write a temporary JSDOM/runtime probe or inspect existing route tests to answer:

- Navigate to the claimed route.
- Stub the preload bridge APIs used by the route.
- Select the relevant row/entity.
- Assert the action button exists.
- Trigger create/edit prompts or handlers.
- Assert the preload bridge method was called with the expected payload.
- Assert no `ReferenceError` occurs on success refresh.

## Verdict guidance

Use BLOCKED when an acceptance criterion says the operator can add/edit/list data but the rendered route does not expose the action, passes the wrong entity shape, calls undefined refresh functions, or has no reachable edit path.

Use PASS WITH NOTES only when the UI path is reachable and correct but evidence is limited to component/JSDOM validation rather than full visual/manual QA.
