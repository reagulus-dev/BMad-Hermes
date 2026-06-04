# Sprint-Status-Led Story Selection and Artifact Creation

## Context

When transitioning between stories (e.g., from HLX-3.1 to HLX-3.2), the workflow must be:
- Explicit in state.
- Aligned with epics_and_stories.md.
- Grounded in existing code.

## Pattern (from Helix: HLX-3.2 selection)

1. Run bmad-sprint-status:
   - Confirm previous story completion (e.g., HLX-3.1 review_passed_with_notes → completed).
   - Select next story as current_story (e.g., HLX-3.2).
   - Update:
     - _bmad/state.json: current_story
     - _bmad/sprint-status.yaml: current_story + add story entry with status: in_progress

2. Read the story’s epics_and_stories.md entry:
   - Use its scope, acceptance criteria, dependencies, and traceability as the canonical base.
   - Do not invent new scope; expand into an implementation-ready artifact.

3. Inspect existing code:
   - Example: check Electron renderer (nav-init.js), vendor registry (@helix/vendors), navigation config.
   - Use this to:
     - Confirm what is already implemented vs placeholder.
     - Make acceptance criteria concrete and technically plausible.
     - Define “Out of Scope” clearly (e.g., no runtime integration, no future stories’ work).

4. Create/update the story artifact:
   - Path: _bmad/artifacts/stories/HLX-3.2-build-vendor-modules-ui.md
   - Include:
     - Metadata (artifact_type, epic, dependencies, traceability)
     - Story
     - Concrete scope and implementation expectations
     - Acceptance criteria as checklist
     - Out of Scope
     - Evidence requirements
     - Next recommended workflows (e.g., bmad-dev-story, bmad-code-review)

5. Synchronize state:
   - state.json:
     - current_story: HLX-3.2
     - workflow_status: story_created
     - next_recommended_workflows: ["bmad-dev-story for HLX-3.2"]
   - sprint-status.yaml:
     - Ensure HLX-3.2 is in_progress and current_story.

## Key Rules

- Never create a story artifact before formally selecting it via sprint-status.
- Always derive from epics_and_stories.md; do not freeform.
- Always ground acceptance criteria in the actual codebase.
