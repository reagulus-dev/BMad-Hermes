# Authorized review supersedes invalid model review

Use when the user says a prior BMad review was unauthorized because it used the wrong model/provider, even if that review already committed a passing status and artifact updates.

## Pattern from HLX-5.5

Situation:
- A prior reviewer using Qwen3.6 produced a `PASS WITH NOTES` review and committed BMad artifact updates.
- The user explicitly invalidated that review because it was unauthorized for `bmad-code-review`.
- The code correction itself was valid; the problem was the review provenance and progression anchor.

Required handling:
1. Treat the unauthorized review verdict as invalid as a progression gate, not as evidence to rubber-stamp.
2. Re-read repo truth: story artifact, state, sprint status, continuation doc, implementation, tests, recent commits, and prior BLOCKED sections.
3. Re-run focused validation rather than copying the invalid validation summary:
   - focused package tests for the touched area;
   - touched package typecheck/build when practical;
   - workspace typecheck if cheap enough;
   - machine-readable artifact parses;
   - `git diff --check`.
4. Append a new authorized review section to the story artifact that explicitly names the invalid review section/commit and says it is superseded.
5. Re-anchor every status layer to the authorized review:
   - story frontmatter status and updated_at;
   - `_bmad/state.json` last_review_summary / active_workflow / next_recommended_workflows;
   - `_bmad/sprint-status.yaml` evidence anchor, review_notes, validation_summary;
   - `CONTINUE-HERE.md` top status.
6. Commit the superseding review/artifact update as its own docs commit when the repo workflow expects clean state.

## Pitfalls

- If the invalid review commit is also current HEAD, say `authorized review at HEAD <sha> supersedes unauthorized review commit <sha>` and make clear the code state is being reviewed fresh; the same SHA can name both the current code/artifact state and the invalid review artifact being superseded.
- Do not leave story frontmatter stale. In HLX-5.5, the body/state showed pass-like status while story frontmatter still said `review_blocked`; the authorized review fixed frontmatter to `review_passed_with_notes`.
- Do not serialize large YAML wholesale just to change one story block. Use targeted edits and then parse the whole YAML.
- Do not record setup-only glitches as blockers. If `python` is missing but `python3` parses artifacts successfully, record it as tooling-only or omit it from final status.

## Review wording snippet

```
Invalid prior review handling:
- The prior `<review section/commit>` was produced by an unauthorized `<model/provider>` reviewer and is treated as invalid as a progression gate.
- This fresh authorized review supersedes that prior verdict and re-inspects the story from repo truth rather than reusing its conclusion.
```
