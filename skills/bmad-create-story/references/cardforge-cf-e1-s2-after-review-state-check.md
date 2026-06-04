# CardForge CF-E1-S2 After Review State-Check Pattern

Session pattern for moving from a freshly reviewed scaffold story into the next canonical story.

## Trigger

Use when:
- The user asks to run `bmad-state-check` after a `PASS WITH NOTES` code review.
- They explicitly say to proceed to the next workflow if no blockers, usually `bmad-create-story`.
- The prior story has non-blocking carry-forward notes but no blockers.

## Pattern

1. Run the state check from repo truth:
   - `git status --short`
   - recent commits / HEAD
   - `_bmad/state.json`
   - `_bmad/sprint-status.yaml`
   - current story artifact
   - planning artifact `epics_and_stories.md`
2. Classify the prior story:
   - If fresh review evidence exists and blockers are empty, trust `PASS WITH NOTES` as sufficient for progression.
   - Do not convert non-blocking notes into correction work unless the artifacts or user mark them as blockers.
3. Select the next story from canonical planning:
   - Use the next pending story in `epics_and_stories.md` / sprint status.
   - For CardForge, CF-E1-S1 progressed to CF-E1-S2.
4. Create the new story artifact with:
   - State-check / selection rationale.
   - Canonical source quote from `epics_and_stories.md`.
   - Scope, implementation expectations, AC checklist, out-of-scope, evidence requirements, dev notes.
   - Explicit carry-forward disposition from the prior story.
5. Reconcile status layers:
   - Prior story frontmatter can move from `review_passed_with_notes` to `completed` once the next story is selected, while preserving `review_verdict: PASS_WITH_NOTES` in sprint status.
   - Keep `qa_verdict: NOT_QA_VERIFIED` if QA/runtime was not performed; do not imply QA or founder-review readiness.
   - Set `_bmad/state.json.current_story` and sprint `current_story` to the new story.
   - Set `workflow_status: story_created`, `active_workflow: bmad-dev-story`, and next workflow to `bmad-dev-story for <story>`.
   - Add the previous story to `completed_stories` where the project uses that field.
6. Update continuation docs concisely:
   - Current status.
   - Previous story verdict and carry-forward notes.
   - New story artifact/status/next workflow.
7. Validate and commit:
   - Parse `_bmad/state.json`.
   - Parse `_bmad/sprint-status.yaml`.
   - Parse frontmatter for touched story artifacts.
   - Run `git diff --check` before committing.
   - Commit the story creation/reconciliation as a docs/story artifact commit.

## Important Pitfalls

- `PASS WITH NOTES` is not QA success. Preserve `NOT_QA_VERIFIED` unless a separate QA gate ran.
- Carry-forward notes should travel into the new story when relevant, but they should not automatically block progression.
- Do not leave `CONTINUE-HERE.md` recommending the previous review workflow after sprint/state have moved to the new story.
- Keep sprint-status edits targeted; avoid full YAML reserialization churn.
