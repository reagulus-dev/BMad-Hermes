# Epic transition after a bridge/tech-debt review

Session example: Helix moved from `HLX-TECHDEBT-2` into Epic 5 and created `HLX-5.1`.

## When this applies

Use this pattern when the previous story is a bridge/tech-debt cleanup that has passed `bmad-code-review` and the next story is the first story in a new epic.

## Pattern

1. Run/perform state check before story creation:
   - Confirm the bridge story status is review-passed or completed enough for handoff.
   - Confirm blockers are empty.
   - Confirm the next story is canonical in `epics_and_stories.md` and no artifact already exists.
   - Confirm dependencies have passed their gates.

2. Create the next story artifact with explicit transition context:
   - Include a short “BMad State Check” section with timestamp, verdict, no-blocker statement, and selection rationale.
   - Reference the bridge story review evidence and canonical planning/architecture/PRD anchors.
   - Make the new epic boundary explicit, especially what is out of scope.

3. Synchronize state artifacts:
   - `_bmad/state.json`: `workflow_status=story_created`, `active_workflow=bmad-create-story`, `current_epic`, `current_story`, `next_recommended_workflows=["bmad-dev-story for <story>"]`.
   - `_bmad/sprint-status.yaml`: update top-level `current_epic/current_story`, append the new story entry, and keep the previous bridge story’s review evidence intact.
   - `CONTINUE-HERE.md`: rewrite the top checkpoint and early active-story section so they point to the newly created story and next workflow.

4. Preserve evidence boundaries:
   - Do not convert static/code-review evidence into runtime/founder-readiness claims.
   - Carry unverified runtime claims forward as explicitly unclaimed when relevant.

## Pitfalls

- Do not let a bridge story’s `PASS WITH NOTES` remain as the “current story” after creating the next epic story.
- Avoid rewriting all of `_bmad/sprint-status.yaml` via generic YAML dump when only a small append/update is needed; it causes noisy diffs. Prefer targeted text edits or a style-preserving YAML tool.
- If a first attempt reformats a large YAML artifact, revert that file and reapply a minimal targeted patch before committing.
- Do not invent a non-canonical intermediate story (for example a stale `HLX-4.6`) when the canonical plan says the next story is the first story of the next epic.

## Verification checklist

- New story exists and frontmatter parses as YAML.
- `_bmad/state.json` parses and points to the new story.
- `_bmad/sprint-status.yaml` parses, points to the new story, and contains the new story entry.
- `CONTINUE-HERE.md` top/current sections point to the new story and next workflow.
- `git diff --check` passes before commit/reporting.
