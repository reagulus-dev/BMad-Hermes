# Helix Epic 4 BMad Status Gate Pattern

Session-derived example for auditing whether a BMad story is ready for the next workflow gate.

## Trigger

Use this pattern when the user says a prior `bmad-dev-story` may have completed and asks whether the project should now be at `bmad-code-review`, or asks "where are we now" for a BMad project.

## Artifact Cross-Check

For Helix-like BMad projects, confirm all of these before reporting the next workflow:

1. `_bmad/state.json`
   - `current_story`
   - `active_workflow`
   - `workflow_status`
   - `next_recommended_workflows`
2. `_bmad/sprint-status.yaml`
   - story status
   - review verdict
   - QA/runtime verdict if present
   - story artifact path
3. Story artifact under `_bmad/artifacts/stories/`
   - status header
   - acceptance criteria checkboxes
   - implementation notes/evidence section
   - review findings section, if already reviewed
4. `CONTINUE-HERE.md`
   - whether it agrees with live state and sprint status
   - whether it contains stale guidance that needs reconciliation
5. Git state
   - current branch
   - dirty worktree vs committed state
   - latest commit when the user asks where the repo was left

## Interpretation Pattern

- `bmad-dev-story` + `implemented_not_reviewed` + checked acceptance criteria + implementation evidence => next workflow is `bmad-code-review`.
- `bmad-code-review` completed with `PASS WITH NOTES` and no blockers => mark story completed, preserve carry-forward notes, then advance to the next story creation workflow.
- `PASS WITH NOTES` is not the same as correction required. Only reopen implementation if the artifacts identify blockers or the user explicitly asks for cleanup.
- For pure scheduler/static package work with no Electron, DB, Redis, browser, vendor-network, or checkout boundary, runtime QA may be recorded as not applicable; do not invent runtime evidence.

## Reconciliation After Review

When the review gate closes, update all status layers together:

- story artifact status/review section
- `_bmad/state.json`
- `_bmad/sprint-status.yaml`
- `CONTINUE-HERE.md`

Then validate JSON/YAML parseability and run an appropriate lightweight whitespace check such as `git diff --check` before claiming reconciliation is complete.

## Carry-Forward Example

HLX-4.1 produced a non-blocking carry-forward note: `validateVendorRequestBudget` existed as an explicit helper and future concrete monitor configuration/start wiring must call it. This belonged in the completed story's review notes and future-story context, not as a blocker on the pure scheduler story.
