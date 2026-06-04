# Carry-forward notes into the next canonical story (HLX-5.4 pattern)

Use this when a story passes `bmad-code-review` with **PASS WITH NOTES** and the notes are explicitly non-blocking, but the next planned story is the natural place to close them.

## Trigger

- Previous story status is `review_passed_with_notes` / PASS WITH NOTES.
- No blocker remains and no dedicated cleanup story is warranted.
- The carry-forward notes map directly to the next canonical story in `epics_and_stories.md`.
- The user asks to run `bmad-state-check` and then `bmad-create-story` with carry-forward notes included.

## Procedure

1. Run/record a state check before story creation:
   - Confirm previous review gate passed with notes and no blockers.
   - Confirm the named/next story exists in `epics_and_stories.md`.
   - Confirm no story artifact already exists for the target story.
   - Identify the current code reality that makes the carry-forward notes relevant.

2. Create the new story artifact with a dedicated `BMad State Check` section:
   - Selection rationale.
   - Current code reality.
   - Evidence/runtime boundary.
   - Why the carry-forward notes belong in this story rather than a cleanup story.

3. Embed carry-forward notes in actionable places, not only prose:
   - Scope: what must be absorbed.
   - Acceptance Criteria: how it will be verified.
   - Tasks/Subtasks: implementation steps.
   - Dev Notes: explicit pitfalls and boundaries.
   - Evidence Requirements: validation commands or artifact checks.

4. Synchronize state layers with focused edits:
   - `_bmad/state.json`: `current_story`, `workflow_status: story_created`, `active_workflow: bmad-dev-story`, `next_recommended_workflows`.
   - `_bmad/sprint-status.yaml`: `current_story`, add target story entry, preserve existing YAML style and avoid broad dumper rewrites.
   - `CONTINUE-HERE.md`: top current status and early active-story/next-workflow sections.

5. Validate before and after commit:
   - Parse state JSON.
   - Parse sprint YAML.
   - Parse story frontmatter.
   - Assert the carry-forward note phrases appear in the new story.
   - Run `git diff --check`.
   - After commit, rerun lightweight consistency assertions and confirm a clean tree.

## Pitfalls

- Do not convert PASS WITH NOTES into a same-story correction unless artifacts or the user mark the notes as blockers.
- Do not leave continuation docs pointing at the old review workflow after selecting the new story.
- Do not update the previous story's own timestamp unless you are materially editing that story.
- Do not rewrite the entire sprint YAML with a generic formatter; targeted text edits keep the semantic change reviewable.
- Do not bury critical carry-forward notes only in `carry_forward_notes`; mirror them in the new story's AC/tasks/dev notes so the dev agent cannot miss them.
