# Next-story creation after review pass pattern (2026-05-20)

Use when a story just passed `bmad-code-review` and the user asks to run `bmad-state-check` and proceed with `bmad-create-story` if no blockers.

## Pattern

1. Run the state/sprint check first; do not jump straight to story writing.
2. Confirm the prior story status across:
   - `_bmad/state.json`
   - `_bmad/sprint-status.yaml`
   - prior story artifact
   - continuation doc top section
   - clean git status / recent HEAD if committing artifacts
3. Select the next story from canonical planning (`epics_and_stories.md`) rather than memory.
4. Verify no story artifact already exists for the selected ID.
5. Create the story with a `BMad State Check` section that records:
   - no-blocker result
   - prior review status and evidence boundary
   - why this story is next
   - what remains unclaimed from previous pure/static slices
6. Keep the new story scope explicitly bounded. For pure orchestration/lifecycle stories, call out runtime/browser/vendor/payment/verification/final-submit surfaces as out of scope unless they are genuinely in this story.
7. Update synchronized state layers:
   - new story artifact frontmatter/status
   - `_bmad/state.json`: `current_story`, `workflow_status: story_created`, `active_workflow: bmad-dev-story`, `next_recommended_workflows`
   - `_bmad/sprint-status.yaml`: append/update the new story entry and current story pointer without broad YAML reformatting
   - `CONTINUE-HERE.md`: rewrite the current-status top section to the new story and next workflow
8. Validate before commit:
   - JSON parse `_bmad/state.json`
   - YAML parse `_bmad/sprint-status.yaml`
   - YAML parse new story frontmatter
   - `git diff --check`
9. Commit the artifact handoff when the user asked to proceed with the workflow and repo history is being maintained.

## Example outcome

After `HLX-5.1` passed review with notes, `HLX-5.2 — Implement checkout worker lifecycle state machine` was selected from Epic 5. The new story artifact captured a pure state-machine scope: valid/invalid transitions, durable transition/event handoff shapes, rehydration semantics, and focused tests. It explicitly excluded browser/profile launch, add-to-cart/cart/checkout, payment, CAPTCHA/OTP/3DS/SCA runtime handling, final submit, live Redis runtime, and Checkout Workers UI.

## Compaction/todo pitfall

If a context compaction restores an old task list showing selection/creation as still pending, compare against actual artifacts and git status first. If the files already exist and parse, mark those todo items completed and continue with validation/commit instead of recreating or reselecting.
