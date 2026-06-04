# Post-review next-story creation with a missing technical plan

Use this pattern when a prior story has just passed code review and the user asks to create the next story.

## Trigger

- `_bmad/state.json` still names the reviewed story as `current_story` with a boundary state such as `review_passed_with_notes`.
- `_bmad/sprint-status.yaml` marks that story `completed` and the next planned story is blocked/ready to unblock.
- The BMad consistency validator may initially fail because the active `current_story` is terminal/completed while state still represents the post-review boundary.
- The planning entry for the next story references a technical plan/source artifact that is missing or empty.

## Pattern

1. Treat the validator failure as a selection-boundary drift, not as a product blocker, when:
   - the prior review verdict is recorded in the story artifact and sprint YAML;
   - the prior story is listed in `completed_stories`;
   - the user explicitly asked to move to the next story.
2. Read the canonical `epics_and_stories.md` entry for the requested next story and inspect nearby code boundaries so the new story reflects current implementation reality.
3. If the next story's canonical planning/source artifact is referenced but missing or empty, create a concise grounding plan before the story artifact. Keep it class-level and architectural, not an implementation patch:
   - current architecture facts;
   - this story's bounded shape;
   - explicit future-story boundary;
   - evidence expectations.
4. Create the story artifact under `_bmad/artifacts/stories/` and mark it `ready_for_dev`.
5. In one coordinated edit, update:
   - `epics_and_stories.md` story statuses/links;
   - `_bmad/sprint-status.yaml` top-level `current_story` and the new story block;
   - `_bmad/state.json` (`workflow_status: story_created`, `active_workflow: bmad-dev-story`, `active_story_artifact`, `next_recommended_workflows`);
   - `CONTINUE-HERE.md` current status and active/next workflow.
6. Run the BMad consistency validator after the edit; it should now pass because the new current story is non-terminal and ready for dev.

## Pitfalls

- Do not re-run the previous code review just because the validator reports drift at the handoff boundary.
- Do not leave a missing referenced source plan for the dev-story agent to discover later; create a concise plan if the next story depends on it.
- Do not absorb the blocked sibling/future story into the new story just because you are creating a technical plan. Record the boundary explicitly.
- Keep sprint YAML edits targeted; do not reserialize the whole file.
