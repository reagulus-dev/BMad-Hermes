# M2.7 bounded correction delegation notes

Use this reference when asking a cheaper/weaker subagent model (for example MiniMax M2.7) to execute a BMad dev-story correction. The failure mode observed in-session was that a broadly worded "bmad-dev-story correction" request was misread as a code-review task, and the subagent reported a review-style outcome instead of doing the bounded correction work.

## Prompt shape that works better

Give the subagent a narrow, self-contained correction brief:

1. **Name the workflow and non-goal explicitly**
   - "Run `bmad-dev-story` correction for story `<ID>`."
   - "This is not `bmad-code-review`; do not produce only a review verdict."
2. **State the exact objective**
   - Identify the specific defect/gap to correct.
   - List the acceptance criteria that must become true.
3. **Bound the writable surface**
   - Name the files/directories the subagent may edit.
   - Name files/directories that are read-only or out of scope.
4. **Require artifact reconciliation**
   - Update the story artifact, `_bmad/state.json`, sprint/status artifacts, and continuation notes only if the code/test result justifies it.
   - Keep status truthful: blocked/deferred/pass-with-notes is allowed; false completion is not.
5. **Require concrete validation evidence**
   - Run the smallest relevant tests first, then the project validation bundle if appropriate.
   - Report exact commands and pass/fail output summaries.
6. **Constrain the final report**
   - Return: files changed, commands run, acceptance criteria status, remaining blockers/notes.
   - Do not include broad unrelated code-review commentary.

## Compact reusable delegation prompt

```text
You are executing BMad workflow `bmad-dev-story` as a correction pass for story <STORY_ID> in <PROJECT_ROOT>.

This is NOT `bmad-code-review`. Do not stop at a review verdict. Your job is to make the bounded correction needed for this story, validate it, and reconcile artifacts truthfully.

Scope:
- Read: <story artifact>, _bmad/state.json, _bmad/sprint-status.yaml, CONTINUE-HERE.md, and relevant source/tests.
- May edit: <specific source/test/artifact paths>.
- Do not edit: <out-of-scope paths>.

Correction objective:
- <specific defect/gap>

Acceptance criteria:
- <AC1>
- <AC2>

Required process:
1. Inspect the listed artifacts and current code.
2. Implement only the correction needed for the objective.
3. Add/update focused tests if needed.
4. Run focused validation, then the agreed full validation bundle if appropriate.
5. Reconcile BMad artifacts only to match verified reality.

Final response must include:
- Summary of correction performed.
- Files changed.
- Validation commands and results.
- Acceptance criteria status.
- Remaining blockers or notes.
```
