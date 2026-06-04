# Renderer Async CRUD/UI Review

Use this reference when reviewing Electron/browser renderer CRUD flows backed by preload/IPC/service calls.

## Durable lesson

Passing renderer tests can still hide runtime races when the test mocks resolve synchronously or when assertions wait with arbitrary timers. For operator-facing add/list/edit acceptance criteria, review the async sequencing of the rendered route, not just whether helper functions exist or a fast mock passes.

## Review checklist

- On selection/change handlers that load entity-specific data, check whether the async loader is awaited before rendering the detail panel.
- If the loader is intentionally fire-and-forget, verify it triggers a deterministic follow-up render after the data arrives.
- Ensure stale responses cannot populate the currently selected detail for the wrong parent entity after rapid selection changes.
- Add at least one delayed-resolution regression test for UI-facing list/detail data:
  - mock the preload call with a delayed promise;
  - select/open the parent entity through the real rendered route;
  - resolve/wait for the promise;
  - assert the child row/action appears in the DOM.
- Avoid trusting fixed `setTimeout(50)` tests alone; they can pass with fast mocks while real IPC/database calls arrive later.

## BLOCKED criteria

Use `BLOCKED` when an acceptance criterion says the operator can see/list/edit child data but the render path only updates state after async load completion without a re-render, or otherwise depends on a race between IPC resolution and immediate render.

## Correction pattern

Either:

```js
onClick: async () => {
  selectedParentId = parent.id;
  await loadChildrenForParent(parent.id);
  await renderParentPage();
}
```

or:

```js
onClick: () => {
  selectedParentId = parent.id;
  renderParentPage();
  loadChildrenForParent(parent.id).then(() => {
    if (selectedParentId === parent.id) renderParentPage();
  });
}
```

Prefer the second form when the UI should show a loading/empty state immediately, but include stale-selection guards.
