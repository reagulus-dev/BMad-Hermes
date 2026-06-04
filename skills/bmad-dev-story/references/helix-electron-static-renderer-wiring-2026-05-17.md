# Static Electron Renderer Wiring Pitfalls (Helix HLX-3.4)

Context:
- Project: Helix (TS monorepo, Electron desktop app with static renderer shell).
- Story: HLX-3.4 — Add target/product setup with price/cart guardrails.
- Review: BLOCKED due to renderer wiring defects that passed typecheck and build.

These defects are class-level: they will recur in any Electron app that uses a static renderer (nav-init.js–style) with custom createElement and CRUD flows.

## 1. createElement ignores options.children

Symptom:
- A section header or button group is defined using options.children but never appears in DOM.
- Happens when createElement(tag, options, children) only appends from the third argument.

Fix:
- Merge both sources:

  - const allChildren = Array.isArray(options.children)
      ? [...(Array.isArray(children) ? children : []), ...(options.children || [])]
      : children;
  - for (const child of allChildren) element.appendChild(child);

Signal for review:
- Any UI that uses options.children but lacks positional children is a red flag.

## 2. Detail function receives ID instead of object

Symptom:
- taskGroupDetail(selectedTaskGroupId) is called where selectedTaskGroupId is a string.
- Inside taskGroupDetail, group.name, group.id, etc. are undefined, breaking detail and child actions.

Fix:
- Resolve the object before passing:

  - taskGroupDetail(
      selectedTaskGroupId
        ? taskGroups.find((g) => g.id === selectedTaskGroupId)
        : null
    );

Signal for review:
- Any detail(...) call where the argument is named like selectedSomethingId is suspect.

## 3. Refresh calls using wrong function names

Symptom:
- After create/edit, code calls refreshTaskGroups(), but the actual renderer function is renderTaskGroups().
- Fails silently or throws at runtime; no refresh of list/detail.

Fix:
- Use the real renderer refresh function: await renderTaskGroups().
- Confirm via focused JSDOM test that create/edit triggers the refresh and list updates.

Signal for review:
- Any refreshX() call not defined in the same file is a red flag.

## 4. Unreachable edit flows

Symptom:
- editTarget(id) exists, but target rows are rendered as static text; no button or click handler.
- Acceptance criteria “operator can edit” is not met.

Fix:
- Render explicit Edit buttons per row:
  - createElement('button', {
      textContent: 'Edit',
      attrs: { 'data-testid': `target-edit-${t.id}` },
      onClick: () => editTarget(t.id),
    });
- Add JSDOM tests:
  - Select parent row.
  - Click Edit button.
  - Assert helixTargets.update was called.

Signal for review:
- Any editX function with no corresponding interactive element in the renderer is a blocker.

## 5. Testing expectations

For Electron renderer CRUD UI:
- Do not rely on component compilation as wiring evidence.
- Add JSDOM tests in the renderer test file (e.g., nav-init.test.ts):
  - Verify:
    - Add button is rendered after selecting a parent row.
    - Edit button is rendered per child row.
    - Add button click calls create API.
    - Edit button click calls update API.
- These are cheap and directly validate acceptance criteria that “operator can add/edit.”
