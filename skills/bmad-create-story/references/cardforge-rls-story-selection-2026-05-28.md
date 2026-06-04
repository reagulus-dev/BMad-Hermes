# CardForge: CF-E2-S3 RLS Story Selection (2026-05-28)

Pattern: selecting the next canonical story after the prior story has passed review, then creating the story artifact and reconciling all BMad artifacts.

Trigger:
- Prior story completed at code-review gate (e.g., CF-E2-S2: PASS_WITH_NOTES, N1–N3 addressed).
- state.json and sprint-status.yaml indicate next work (e.g., CF-E2-S3).
- CONTINUE-HERE.md still points to the old story.

Steps:
1. Confirm:
   - state.json:
     - current_epic, current_story, completed_stories.
   - sprint-status.yaml:
     - current_epic, current_story.
   - epics_and_stories.md:
     - next story is defined and not repurposed.
2. Create story artifact:
   - Use epics_and_stories.md as canonical source.
   - Expand into implementation-ready artifact:
     - Story, Scope, Acceptance Criteria, Out of Scope, Implementation Expectations, Evidence Requirements, Next Recommended Workflows.
3. Synchronize:
   - state.json:
     - current_story → new story.
     - active_workflow → bmad-dev-story.
     - workflow_status → story_created.
     - active_story_artifact → new artifact.
     - next_recommended_workflows → bmad-dev-story for <NEW>.
   - sprint-status.yaml:
     - current_story → new story.
     - Mark story status: ready_for_dev.
     - Add story_artifact path.
   - CONTINUE-HERE.md:
     - Update “Current Epic and Story” to new story.
     - Mark prior story as completed (if not already).
     - Update “Remaining Key Risks” if relevant (e.g., RLS now active).

Key rules:
- Do not invent new scope beyond epics_and_stories.md.
- Do not repurpose a future story to absorb gaps; use a continuation story if needed.
- Keep diffs focused; no blanket YAML rewrites.
