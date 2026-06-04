# Electron Renderer Static CRUD UI Pattern (HLX-3.3)

Context:
- Helix (TS/Electron monorepo), story HLX-3.3: Task Groups UI.
- DB migration and repository existed, but wiring them into the renderer was deferred.

Pattern:
- For early Electron renderer CRUD/list-create UI stories where DB wiring is not yet required:
  - Implement the UI in the renderer (nav-init.js or equivalent) with:
    - A small in-memory data store (e.g., taskGroups array).
    - A canonical example row (e.g., Pokémon Center UK task group) to show non-empty state.
  - List view:
    - Table columns aligned with story fields (Name, Vendor, Status, Cadence, Alerts, Tags).
    - Clear empty-state text matching acceptance criteria.
  - Detail view:
    - All fields displayed compactly.
    - Actions: Edit, Duplicate, Start/Stop, View logs, Export/Import config.
    - Logs/Export/Import can be labeled placeholders (Coming soon) with no deep wiring.
  - Create/Edit:
    - Use simple prompts or inline forms.
    - Enforce required fields (e.g., name, vendor_module_key).
  - Duplicate:
    - Copy non-secret config, add “(copy)” suffix, set status to “stopped” or “draft”.
  - Start/Stop:
    - Toggle status field; persist only in memory until DB wiring story.
- Keep:
  - No Node/DB imports in the renderer.
  - Future DB wiring as an explicit out-of-scope note in the story.
- Validate:
  - Add a test that:
    - Navigates to the route.
    - Confirms list view and at least one canonical row.

Outcome:
- Satisfies UI-related acceptance criteria and provides visible structure.
- Leaves a clean integration point for later DB wiring (HLX-3.4+).
