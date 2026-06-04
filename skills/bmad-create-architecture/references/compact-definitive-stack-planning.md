# Compact Definitive Stack Planning Pattern

Use this pattern when a newly initialized BMad project is about to scaffold but only has lightweight seed context, and the user wants to avoid implementation drift.

## Trigger

- Project has `_bmad/project_context.md`, `sprint-status.yaml`, and/or `CONTINUE-HERE.md`, but no canonical PRD/UX/architecture.
- First implementation story is a tech-stack/scaffolding story.
- User asks for a definitive plan or says not to provide options/selection.

## Pattern

1. Treat lightweight context as seed input, not as enough planning for normal BMad implementation.
2. Run a compact planning pass before scaffolding:
   - PRD
   - PRD validation report
   - UX design
   - Architecture
   - Epics and stories
3. In the PRD and architecture, make one definitive stack decision. Do not present multiple options when the user explicitly asked for a single best stack.
4. Record the selected stack in all state-bearing places that future agents will read:
   - PRD
   - Architecture
   - `_bmad/state.json`
   - `CONTINUE-HERE.md`
   - scaffold story artifact
5. Explicitly exclude common drift vectors in the architecture, such as alternate API layers, monorepos, custom auth, separate design systems, or unrelated platforms, unless intentionally selected.
6. Only after planning is complete, create the first scaffolding story artifact and mark it `ready_for_dev`.

## Story Boundary

The first scaffold story should establish the app shell, package manager, routes, directories, environment placeholders, and validation scripts. It should not implement business workflows, full data models, analytics, exports, or integrations.

## Verification

Before handoff, verify:

- Planning artifacts exist at their canonical paths.
- `_bmad/state.json` has normalized fields and points to the current story.
- `sprint-status.yaml` current story matches state.
- `CONTINUE-HERE.md` names the same current story and selected stack.
- The app scaffold has not been accidentally implemented during planning/story creation.
