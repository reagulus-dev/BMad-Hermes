# Electron Renderer: Async Child Data Loading (2026-05-17)

## Context

During HLX-3.4, the Task Groups → Targets detail panel had an async race:
- On task group row click:
  - loadTargetsForTaskGroup(group.id) was called without await.
  - renderTaskGroups() ran immediately.
- If helixTargets.listByTaskGroup() was delayed, selectedTaskGroupTargets was populated after the detail panel had already rendered with no targets.

## Pattern

For Electron renderer CRUD that loads child data asynchronously:
- Parent selection handlers must:
  - Await the child-data load before rendering the detail, or
  - Trigger a deterministic follow-up render after the load completes.
- Do not fire-and-forget an async load and then immediately render.

## Regression Test Requirement

Add a focused regression test:
- Mock the child-data API (e.g., helixTargets.listByTaskGroup) with a short delay (20–50ms).
- Simulate selecting the parent row.
- Wait longer than the delay.
- Assert child rows appear (e.g., via target-edit button or similar data-testid).

This ensures the UI is robust when IPC/DB responses are not instant.
