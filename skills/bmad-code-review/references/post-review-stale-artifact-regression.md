# Post-review stale artifact regression pattern

Use when a story already has a fresh authorized code-review verdict, but later same-session/subagent activity leaves BMad artifacts regressed to an older state (for example `implemented_not_reviewed`, `review_blocked`, or stale `next_workflow` text) before the next state-check/story-creation step.

## Signal

- Source implementation and review commit still support the passing verdict.
- `_bmad/state.json`, `_bmad/sprint-status.yaml`, the story artifact, or `CONTINUE-HERE.md` disagree with each other after a later agent/tool run.
- The regression looks like an artifact overwrite, not a new source-code finding.
- A later workflow is about to select/create the next story, so stale review status would poison progression evidence.

## Required handling

1. Treat the committed story/review evidence and current repo truth as authoritative; do not advance from stale working-tree artifacts.
2. Inspect the uncommitted diff and identify whether it is only a stale BMad artifact regression or includes real source changes.
3. If it is artifact-only regression, restore/reconcile the BMad artifacts to the fresh authorized review verdict instead of re-blocking the story.
4. Before selecting/creating the next story, verify:
   - story artifact status/verdict matches the review section;
   - `_bmad/state.json` current/prior story fields and next workflow are consistent;
   - `_bmad/sprint-status.yaml` has one canonical entry/status for the reviewed story;
   - `CONTINUE-HERE.md` current status does not contain stale duplicate headings or pre-review wording.
5. Parse JSON/YAML/frontmatter and run `git diff --check` after reconciliation.
6. Commit the reconciliation/story-selection update separately when the repo workflow expects clean state.

## Example

CardForge CF-E1-S4 had already reached a fresh authorized `PASS WITH NOTES` code-review state, but a later uncommitted subagent overwrite regressed artifacts back to `implemented_not_reviewed`. The correct response was to restore the committed review-passed artifact state, validate the BMad files, then proceed to state-check and next-story creation from the restored truth rather than treating the stale overwrite as a new product blocker.
