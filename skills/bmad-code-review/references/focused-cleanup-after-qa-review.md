# Focused Cleanup Review After Prior QA

Use this when a story already passed code review and QA/runtime verification, but a small in-scope cleanup correction is run before proceeding to the next epic/story.

## Review stance

- Review only the focused cleanup diff unless the cleanup touches the original runtime-critical path broadly enough to invalidate prior QA.
- Preserve prior QA evidence as historical/runtime evidence, but label it accurately (for example: `RUNTIME VERIFIED BEFORE FOCUSED CLEANUP`).
- Do not silently erase the earlier QA/review thread. Append a fresh review section to the original story artifact.
- Do not claim new runtime/founder/release readiness unless runtime QA was rerun after the cleanup.

## State and sprint-status pattern

Before fresh review:
- `workflow_status`: `implemented_not_reviewed`
- story/sprint `status`: `implemented_not_reviewed`
- `review_verdict`: `PENDING`
- `qa_verdict`: keep prior QA, but qualify it, e.g. `RUNTIME VERIFIED BEFORE FOCUSED CLEANUP`

After fresh code review passes with notes:
- `workflow_status`: `review_passed_with_notes`
- story/sprint `status`: `review_passed_with_notes`
- `review_verdict`: `PASS WITH NOTES`
- `qa_verdict`: keep qualified prior QA unless QA was rerun
- `last_evidence_path`: point to the fresh review section anchor, not only the older QA artifact
- `next_recommended_workflows`: route to state-check / next story selection unless remaining blockers exist

## Validation expectations

- Freshly rerun targeted tests for the cleanup diff.
- Fresh typecheck when the diff touches typed modules or IPC boundaries.
- Parse `_bmad/state.json` and `_bmad/sprint-status.yaml` after edits.
- It is acceptable to cite prior full workspace test/build/migrate evidence if it was produced by the immediately preceding cleanup pass and the review reruns targeted checks/typecheck.

## Common pitfall

Do not mark the story fully `completed` immediately after a focused cleanup review if runtime QA was not rerun after the cleanup. Prefer `review_passed_with_notes` with the prior runtime QA explicitly qualified, then run state-check to decide whether the next workflow is Epic progression or fresh QA.
