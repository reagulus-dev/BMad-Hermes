# Invalid Review Supersession Pattern

Use this when a previous BMad review artifact exists but the user or workflow state says the review was not authorized for that step (for example, an agent ran `bmad-code-review` when only a `bmad-dev-story` correction was requested), or when the review was produced by a model/provider that is not authorized for BMad review (for example a cheaper MiniMax M2.7 role used where the workflow requires the main/high-accuracy review model).

## Review stance

- Treat the unauthorized review verdict as invalid, even if it says `PASS` or `PASS WITH NOTES`.
- If invalidity is model/provider based, do not reuse the unauthorized model's notes as findings to carry forward. They may only guide where to re-inspect during the fresh authorized review.
- Do not merely revert to the previous verdict; run a fresh review from repo truth.
- Read the current story artifact, `_bmad/state.json`, `_bmad/sprint-status.yaml`, continuation docs, recent commits, relevant source files, and focused tests.
- In the new review section, explicitly name the invalid review artifact/commit and state that the fresh review supersedes it.

## Artifact reconciliation

After the fresh verdict:

- Append the valid review under the story artifact's review thread.
- Reconcile story frontmatter/status, `_bmad/state.json`, `_bmad/sprint-status.yaml`, and `CONTINUE-HERE.md` to the new verdict.
- If the fresh review is `BLOCKED`, restore correction routing (`bmad-dev-story correction, then fresh bmad-code-review`) and do not leave stale pass wording from the invalid review.
- If the fresh review reaches the **same verdict** as the invalid review, still add a new superseding review section and update state/status/evidence anchors so future workflow progression is justified by the authorized review, not by the invalid commit.
- If a later state-advance commit already selected the next story based on the invalid pass and the fresh authorized review also passes, preserve the next-story selection when it remains correct, but explicitly rewrite the rationale/continuation text to say the invalid review is superseded by the new authorized review.
- Parse JSON/YAML artifacts and run a cheap diff/whitespace sanity check.
- If the review updates are committed in the repo workflow, use a separate docs/review commit so the repo ends clean.

## Pitfalls

- Do not preserve optimistic `review_passed_with_notes` status just because it was recently committed.
- Do not trust validation summaries from the invalid review without rerunning or independently inspecting the evidence.
- Do not bury the invalid-review context only in the final chat response; it belongs in the story artifact so future agents do not accidentally revive the stale pass state.
