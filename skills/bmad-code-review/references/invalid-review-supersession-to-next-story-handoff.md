# Invalid Review Supersession → Next-Story Handoff

Use when a prior `bmad-code-review` was run without authorization, a fresh authorized review supersedes it, and the workflow then advances to the next canonical story.

## Pattern

1. Treat the unauthorized review as invalid progression evidence, even if its verdict matches the eventual fresh verdict.
2. Run the fresh authorized review from repo truth and append it to the reviewed story artifact.
3. Explicitly name the invalid review artifact/commit and state that the new review supersedes it.
4. Reconcile status/evidence anchors so state, sprint status, continuation docs, and story notes point to the authorized review only.
5. If the fresh verdict is `PASS` or `PASS WITH NOTES`, advance only through the normal next-story workflow:
   - first `bmad-state-check` for canonical next-story selection;
   - then `bmad-create-story` if no blockers and the next story artifact does not already exist.
6. Do not roll back a correct next-story selection solely because the invalid review existed. Instead, revalidate that the fresh review supports progression and rewrite the rationale/evidence anchors to the authorized review.
7. Carry `PASS WITH NOTES` findings forward deliberately:
   - If the next canonical story naturally owns a note, embed it as AC/dev-note/task context in that story.
   - If no canonical story owns it, create or recommend a bounded bridge/cleanup story.
8. Keep runtime/live QA claims explicitly unclaimed unless separately evidenced; do not let a code-review pass imply QA/founder/release readiness.

## Validation bundle

Before finalizing the handoff:
- Parse `_bmad/state.json` as JSON.
- Parse `_bmad/sprint-status.yaml` as YAML.
- Parse the next story frontmatter if a story was created.
- Assert current story, workflow status, active workflow, and sprint entry match the intended state.
- Run `git diff --check`.
- Leave the repo clean with a separate docs/review commit when the project workflow expects committed BMad state.

## Example: HLX-6.1 → HLX-6.2

- Unauthorized prior review: invalid/superseded.
- Authorized fresh review: `PASS WITH NOTES` at commit `38fe45c`.
- Next-story workflow selected `HLX-6.2 — Capture add-to-cart response and cart line state`.
- `HLX-6.1` carry-forward notes were embedded into `HLX-6.2` where relevant:
  - preserve/derive `vendor_module` instead of hardcoding `pokemon_center_uk` in future multi-vendor work;
  - prefer injected adapter/resolver seams over dynamic import runtime wiring;
  - add cross-profile/cart/session boundary tests when adjacent boundaries expand;
  - keep live browser/vendor, Electron/IPC, Redis, DB write, checkout execution, visual QA, and founder-review claims unclaimed unless separately proven.
