# Code Review Mechanics — Local Fallback, Two-Commit Boundary, AC Evidence Mismatch

Companion to `bmad-code-review/SKILL.md`. Three operational patterns that
arise when a delegated review times out, when the configured higher-accuracy
model is not actually wired, or when the review is performed on a working
tree that already has uncommitted implementation changes.

## 1. Local review fallback protocol

When the recommended model routing in the SKILL.md "Model Routing" section
is configured (e.g., `delegation.model: gpt-5.5`,
`delegation.provider: openai-codex`) but the provider is not actually wired
in `~/.hermes/config.yaml`, OR the delegation subagent times out, fall
back to a local review in the current turn rather than asking the user to
set up a new provider. A local review is a valid progression gate when it
covers the same dimensions with the same evidence threshold.

Concretely, the local review checklist is:

1. **Re-run every static gate from a clean tree** (do not trust the Dev
   Agent Record's claim that gates passed):
   - `pnpm prisma:validate` (or repo equivalent)
   - `pnpm prisma:generate` if Prisma
   - `pnpm typecheck` (or `tsc --noEmit` direct)
   - `pnpm lint --max-warnings=0` (the project gate)
   - `pnpm test` (full suite, count deltas vs prior recorded count)
   - `pnpm build`
   - `git diff --check`
2. **Wire-up checks specific to the story's contract** (e.g., for a
   "switch `$transaction` from `prisma` to `prismaDirect`" story, run
   `grep -c 'prisma\.\$transaction'` and `grep -c 'prismaDirect\.\$transaction'`
   to confirm every switched site landed; for a refactor touching N files,
   confirm no read-path leak by grepping for the new symbol in non-target
   contexts). Do not infer "all sites converted" from a diff stat alone.
3. **Read every changed file end-to-end.** Not just the diff — read the
   surrounding context. Look for: hidden imports, dead code, untested
   branches, error handling, retry/backoff assumptions, RLS bypass,
   owner-scope leaks, hardcoded secrets in test fixtures.
4. **Read the story artifact's acceptance criteria one by one** and mark
   each PASS / DEFERRED / NOT-EVIDENCED. Where the dev environment cannot
   exercise a criterion (e.g., live Supabase, live Vercel, real
   third-party OAuth), mark it DEFERRED with an explicit note that
   operator-side re-verification is required. Do not silently PASS.
5. **Classify each story-required test that does not exist in the dev
   environment** as DEFERRED, not PASS. The "AC evidence mismatch"
   pitfall: do not mark a story complete when the AC requires a test or
   runtime check that the dev env cannot exercise, even if you wrote the
   missing test yourself in the review turn (that should be flagged in
   the Required next action, not absorbed into the verdict).
6. **Append the full review to the story artifact** under
   `## Review Findings` with a table of evidence inspected, an explicit
   list of ACs not directly re-verifiable, non-blocking notes (carry
   forward), and the verdict.
7. **Reconcile all four BMad artifact layers** to the verdict: story
   artifact (status frontmatter), `_bmad/sprint-status.yaml` (status,
   review_verdict, qa_verdict, validation_summary, review_notes,
   next_recommended_workflow), `CONTINUE-HERE.md` (Current Status +
   Completed Work), `_bmad/state.json` if it exists.
8. **Route next_recommended_workflow to `bmad-state-check`**, not back to
   `bmad-code-review`. A passing review does not loop.

The local review's evidence threshold is the same as a delegated review's;
the model name on the byline is not what makes the review trustworthy. A
local review with a full evidence table and explicit DEFERRED entries is
more useful than a delegated review that rubber-stamps the Dev Agent
Record.

## 2. Two-commit boundary for uncommitted review work

When the review is performed on a working tree that already has
implementation changes (source/test/docs uncommitted), do not stop at
appending review findings. The user expects two commits: one for the
implementation, one for the review/artifact reconciliation. The boundary
matters because future sessions will inspect `git log` to see what the
review actually passed against, and a future `git revert <review-commit>`
should roll back the verdict without touching the implementation.

Mechanics (concrete recipe):

1. **Snapshot the post-review state of the review-touched files** to
   `/tmp/`:
   - `cp _bmad/sprint-status.yaml /tmp/sprint-postreview.yaml`
   - `cp CONTINUE-HERE.md /tmp/continue-postreview.md`
   - `cp _bmad/artifacts/stories/<id>.md /tmp/story-postreview.md`
2. **Reset the review-state deltas back to implementation state** in
   those files. Concrete reverts:
   - Story frontmatter: `code_review_status: review_passed_with_notes`
     → `pending`.
   - Story body: remove the `## Review Findings (...)` section entirely
     (use `head -N` to truncate to the line before the section heading).
   - Sprint-status: `status: review_passed_with_notes` → `in_progress`,
     `review_verdict: PASS_WITH_NOTES` → `NOT_REVIEWED`,
     `qa_verdict: RUNTIME_SMOKE_OPT_IN_PENDING` → `NOT_QA_VERIFIED`,
     remove `evidence:` field, empty `review_notes`, and set
     `next_recommended_workflow` back to `bmad-dev-story for <id>
     implementation`.
   - CONTINUE-HERE: replace the post-review Current Status block with
     the pre-review implementation state.
3. **Stage and commit** as the implementation commit
   (e.g., `fix(<id>): ...`). The diff stat on this commit is what the
   review passed against.
4. **Re-apply the review-state deltas** to the same three files using
   the `/tmp/` snapshots as the source of truth. Do not retype the
   review section — copy it back via `cat /tmp/story-postreview.md >
   _bmad/artifacts/stories/<id>.md` and re-stage, or apply targeted
   patches against the in-tree impl state.
5. **Stage and commit** as the review/artifact commit
   (e.g., `docs(<id>): record code review verdict PASS_WITH_NOTES`).
6. **Push** with a single `git push origin <branch>` when the user
   asks. Do not push twice; both commits go in the same push.

Why this matters concretely:

- The implementation commit records what the review passed against, with
  the diff stat and validation evidence matching the code at that
  point.
- The review commit records the verdict independently, anchored to the
  story's `## Review Findings` section.
- A future session reading `git log --stat` can see "code change X passed
  review Y" without ambiguity.
- A future `git revert <review-commit>` cleanly rolls back the verdict
  without touching the implementation. A single-commit equivalent cannot
  be partially reverted; either the implementation or the verdict would
  be wrong together.

## 3. AC evidence mismatch: dev-env cannot exercise the AC

When the story's AC includes a check that the dev sandbox cannot run
(e.g., live Supabase, live Vercel, real third-party OAuth, real payment
processor), do not silently mark the AC as PASS. The pattern:

1. Identify the AC.
2. In the review's "Evidence inspected" table, mark the AC row as
   `DEFERRED` and explain the precondition the dev sandbox lacks.
3. In the review's "ACs not directly re-verifiable" section, list each
   such AC with a one-line operator action that would re-verify it
   post-deploy.
4. In the verdict, classify as `PASS WITH NOTES` (not `PASS`) when the
   only outstanding concern is dev-env limitation, and reference the
   deferred ACs explicitly.
5. In the Required next action, the first item is always the operator's
   post-deploy re-verification of the deferred ACs.

Common misclassification: classifying a deferred AC as PASS because
"the code looks right" or "the test file exists and is structurally
complete." A test file existing in the tree is not the same as the test
having run against the live environment it claims to cover.
