# CardForge CF-E5 → CF-E4 resume handoff pattern

Use when a previously held epic/story should resume after a separate prerequisite epic reaches a code-review completion gate.

## Signal

- Current story has just reached `PASS_WITH_NOTES` at the code-review gate.
- The active epic is now code-review complete, but runtime/founder QA or live migration/API verification remains explicitly unverified.
- Another epic/story was previously marked `on_hold` / `deferred` only until this prerequisite completion condition was met.
- A ready story artifact for the deferred story already exists.

CardForge example: CF-E4 Shopify storefront work was on hold until CF-E5 import/multi-location ergonomics reached code-review completion. After CF-E5-S3 passed with notes, the correct next workflow was to resume CF-E4 and select already-created CF-E4-S3 for `bmad-dev-story`, while preserving no-live-Shopify-claim boundaries.

## Required handling

1. Reconcile the just-reviewed story first:
   - append/anchor the review findings in the story artifact;
   - set the story status and sprint entry to completed / `PASS_WITH_NOTES`;
   - add the story to `completed_stories`;
   - preserve QA/live migration gaps as notes, not blockers.
2. Select the deferred story only after the prerequisite story is reconciled.
3. Update all active pointers together:
   - `_bmad/state.json`: `current_epic`, `current_story`, `current_sprint`, `active_story_artifact`, `workflow_status`, `active_workflow`, `next_recommended_workflows`.
   - `_bmad/sprint-status.yaml`: resume the held epic, mark the selected story `ready_for_dev`, and mark the prerequisite epic completed if all its stories are code-review complete.
   - planning docs and `CONTINUE-HERE.md`: remove stale hold/deferred wording and record the state-check selection rationale.
4. Preserve evidence boundaries explicitly:
   - `PASS_WITH_NOTES` code review is not runtime/founder QA.
   - Mocked Shopify tests are not live Shopify API/dev-store success.
   - Local Prisma validation/build is not live Supabase migration deployment.
5. Run the cross-artifact consistency probe after updating active pointers, not while `current_story` still points at a completed story.
6. Commit reconciliation/story-selection artifacts once JSON/YAML parse, `git diff --check`, and the consistency probe pass.

## Validator pitfall

The validator can correctly fail if `state.json.current_story` still points at a now-completed story while `workflow_status` says a review just passed. Treat that as a handoff-boundary mismatch: finish selecting the next active story, then rerun the validator and require it to pass.
