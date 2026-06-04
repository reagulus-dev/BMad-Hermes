# CardForge CF-E5-S3 post-review story selection pattern

Use when a CardForge/BMad session has just passed a story code review and the user asks to run `bmad-state-check` and proceed with `bmad-create-story` if unblocked.

## Situation

- Prior story: `CF-E5-S2` passed BMad code review with `PASS_WITH_NOTES` and was committed.
- Live `state.json` still had `current_story: CF-E5-S2`, `workflow_status: review_passed_with_notes`, and `active_workflow: bmad-state-check`.
- `sprint-status.yaml` correctly had `CF-E5-S2` as `completed`.
- The BMad artifact consistency probe initially failed because the current story was terminal/completed while state still pointed at it.

## Correct interpretation

Treat this as an expected post-review handoff boundary, not a blocker, if:

1. The current story has a recorded PASS/PASS_WITH_NOTES review.
2. There is no `review_blocked` / correction workflow.
3. Sprint/planning docs identify a canonical next story.
4. The working tree is clean or only contains intended story-selection edits.

## Procedure

1. Confirm git status and latest commit.
2. Run the BMad consistency probe and record any pre-selection handoff drift.
3. Read:
   - `_bmad/state.json`
   - `_bmad/sprint-status.yaml`
   - `_bmad/artifacts/planning/epics_and_stories.md`
   - any epic-specific technical plan.
4. Select the next canonical story from sprint/planning truth.
5. Create the story artifact with a contract-shaped `SKILL.md`-style story body:
   - frontmatter
   - story statement
   - state-check rationale
   - current code reality
   - scoped implementation sections
   - acceptance criteria
   - out-of-scope
   - implementation expectations
   - evidence requirements
   - next workflows
6. Reconcile all layers together:
   - `state.json`: `current_story` -> new story, `workflow_status: story_created`, `active_workflow: bmad-dev-story`, `next_recommended_workflows` -> dev story.
   - `sprint-status.yaml`: new story `ready_for_dev`, prior story remains `completed`.
   - planning doc: update the next story status/artifact path and remove stale “blocked by prior story” wording after selection.
   - continuation doc: top status and active workflow point at the new story.
7. Rerun JSON/YAML parse, BMad consistency probe, and `git diff --check`.
8. Commit with a docs-style story creation message.

## Concrete CF-E5-S3 notes

- The next story was `CF-E5-S3 — Multi-Location Stock Model (Option C)`.
- Story artifact: `_bmad/artifacts/stories/CF-E5-S3-multi-location-stock-model-option-c.md`.
- Scope included additive `CardItemLocation`-style per-bin quantity model, migration/backfill from `CardItem.location`, inventory UI/filter/import rewiring, and regression preservation for CF-E5-S1/S2.
- CF-E4 Shopify work stayed on hold.
- Runtime/founder QA stayed unclaimed.

## Pitfalls

- Do not treat the pre-selection consistency probe failure as a reason to re-review the already-passed story.
- Do not leave anchors like `#cf-e5-s3--...-blocked-by-cf-e5-s2` after the heading is updated to remove “blocked by”. Update `source_artifact` anchors to match the new heading.
- Do not run implementation before the story artifact is physically saved and state/sprint/continuation docs are synchronized.
