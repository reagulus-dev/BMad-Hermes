# CardForge CF-E1-S5 — review pass to state-check/story creation pattern

Use this as a compact example when a story has a fresh BMad code-review verdict, the user asks to commit/advance, and the next canonical story must be selected without overstating QA readiness.

## Durable pattern

1. **Commit the reviewed implementation first** when the user asks to commit all code before advancing.
   - Commit source, focused tests, story review findings, and reconciled BMad artifacts together.
   - Use a conventional commit such as `feat(STORY-ID): implement ...`.
   - Verify clean status after the commit before state-check.
2. **Preserve code-review verdict semantics.**
   - `PASS WITH NOTES` is a code-review gate outcome, not a QA/founder-review/live-RLS pass.
   - Keep deferred runtime/browser/live Supabase/RLS verification explicit in the story, state, sprint status, and continuation doc.
3. **Run state-check from project-local truth.**
   - Read `_bmad/state.json`, `_bmad/sprint-status.yaml`, and canonical planning artifacts.
   - Confirm blockers are empty and the next pending story is canonical before creating it.
   - Search for an existing next-story artifact before creating a new one.
4. **Create the next story only after selection is evidenced.**
   - Set the new story artifact to `ready_for_dev`.
   - Set `_bmad/state.json.workflow_status` to `story_created` and `active_workflow` to `bmad-dev-story` when the story artifact now exists.
   - Set sprint `current_story` to the new story and mark it `ready_for_dev`.
5. **Do lightweight doc-artifact verification for doc-only story creation commits.**
   - Parse JSON/YAML/frontmatter.
   - Run `git diff --check`.
   - Do not rerun the full implementation validation bundle when no application code changed in the story-creation commit; preserve prior validation evidence and state the scope.
6. **Commit story-creation/reconciliation separately.**
   - Use a conventional docs commit such as `docs(NEXT-STORY-ID): create ... story`.
   - Final status should be clean and state/sprint should agree on current story and next workflow.

## Common pitfall

Do not let next-story creation silently turn a `PASS WITH NOTES` code-review result into `QA VERIFIED`, `founder-ready`, or `completed with no caveats`. The right progression can be: reviewed story completed at the code-review gate, next story ready for dev, QA/runtime/live verification still deferred and explicitly unclaimed.
