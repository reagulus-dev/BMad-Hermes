# Async race patterns to watch for

- Handler calls async data loader without await, then immediately:
  - Renders UI.
  - Updates global state or refs.
  - Triggers another async call that depends on that data.
- Fix pattern:
  - Mark handler async.
  - await loadTargetsForTaskGroup(...)
  - then renderTaskGroups() or equivalent.
- Regression test pattern:
  - Mock the data-loading function to delay (e.g., 50–100ms).
  - Trigger the action.
  - After delay, assert that dependent UI/rows/panels exist.
