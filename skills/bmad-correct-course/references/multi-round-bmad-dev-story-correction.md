# Multi-round bmad-dev-story correction — how to handle a fresh BLOCKED on a story that was just corrected

When `bmad-code-review` returns `BLOCKED` on a story whose previous `bmad-dev-story` correction just landed, you are in a **multi-round correction**. This is a distinct workflow from a one-shot correction, with its own pitfalls and a specific "what to do before you start" checklist. This reference captures the patterns that emerged from the CF-E5-S3 second-round correction (2026-06-02) and the meta-patterns for running a second-round cycle efficiently.

## When this applies

Use this reference when ALL of the following are true:

1. The current story has a `bmad-dev-story` correction commit that landed in the last 24-72 hours.
2. The fresh `bmad-code-review` returned `BLOCKED` on **a different shape** of blockers than the previous review (not the same blockers returning, which would be a different problem).
3. `state.json`'s `last_review_summary` records the fresh BLOCKED verdict and `blockers` is non-empty.
4. The story artifact's most recent section is a "Dev Agent Record" with "bmad-dev-story correction" in the heading.

If only some of these are true, you are in a different workflow — see the `bmad-correct-course` decision rules.

## Pre-flight checklist (do this before touching code)

### 1. Re-read the fresh review's BLOCKED findings, not the prior round's correction

The story artifact has both a "first-round Dev Agent Record" and a "fresh review BLOCKED" section. The **fresh review** section is the authoritative scope for this round. The first-round section tells you which patterns are already in the repo (so you do not re-invent `applyMergeStockForOwner` if the second review is about something else), but the new blockers are enumerated in the fresh review.

The CardForge CF-E5-S3 example: the first-round Dev Agent Record said "all three blockers are fixed"; the fresh review said "those three are fixed, but here are four more." If you read only the first-round section, you will think the work is done. The fresh review's findings are the new scope.

### 2. Build a boundary-walk table before writing the first line of code

After the fresh review's findings are clear, list every write path that touches the story's central invariant. The first review usually fixes the path it walked; the second review usually surfaces adjacent paths the first review did not walk. Building the table before the first commit makes the correction 3-5x faster than discovering the next path mid-correction.

CardForge CF-E5-S3 example table (the central invariant is `sum(CardItemLocation.quantity) == CardItem.quantity`):

| Write path | Atomic? | Bucket sum == quantity? | Fixed in which round? |
|---|---|---|---|
| Migration backfill | Yes (1 migration) | Yes (1:1) | Implementation |
| `setLocationForOwner` (bulk action) | Yes (`$transaction`) | Yes (collapse to 1 bucket) | Implementation + cleanup |
| `applyMergeStockForOwner` (CSV merge existing) | Yes (`$transaction` + guard) | Yes | First-round correction |
| `createManyWithInitialBucketsForOwner` (CSV create) | Yes (`$transaction` + guard) | Yes | Second-round correction |
| `createWithInitialBucketForOwner` (manual create) | Yes (`$transaction`) | Yes | Second-round correction |
| `updateQuantityForOwner` (manual edit) | Yes (`$transaction`) | Yes (rebalance) | Second-round correction |
| `deductCardInventoryAndSnapshotCogs` (sales decrement) | Was: no / is: yes (added `adjustBucketQuantitiesForOwner`) | Was: drift / is: yes | Second-round correction |
| `restoreCardInventory` (sales restore / cancel) | Was: no / is: yes | Was: drift / is: yes | Second-round correction |
| Page-level filtered summary | Was: unfiltered / is: narrowed to `summaryItems` | n/a (counted) | Second-round correction |
| `bulkUpdateForOwner` (archive / lot assign) | n/a (no quantity change) | n/a | Pre-existing |

The first round fixed the 3 paths it exercised (highlighted green in the table). The second round fixed the 4 of the 8 untouched paths the fresh review surfaced (highlighted yellow). The boundary walk took 10 minutes; the focused tests + mocking for each new path took the rest of the correction. Skipping the boundary walk would have meant discovering "we forgot the sales service" only after committing the CSV create fix and re-reviewing.

### 3. Audit every existing test that mocks the touched surface

A second-round correction typically adds new repo helpers (or extends existing ones). Every test that mocks `@/lib/db/owner-scope` or `@/lib/db/prisma` needs the new method in its mock surface. Audit and extend in the same commit, because a partial update produces a wave of "Cannot read properties of undefined" failures in the next `pnpm test` run that look like production bugs but are test-fixture gaps.

The mechanical checklist:

1. **Action-level tests** (e.g. `inventory-actions-money.test.ts`, `cf-e2-s2-stabilization.test.ts`): add the new method name to the `vi.mock("@/lib/db/owner-scope")` factory object as `newMethod: vi.fn()`.
2. **Helper-level tests** (e.g. `cf-e5-s3-multi-location-stock.test.ts`): the `vi.mock("@/lib/db/prisma")` factory is the source of truth; new helpers that use `$transaction` need a `txMock` with every method the helper calls.
3. **Sales service / multi-step tests** (e.g. `sales-service.test.ts`): the `mockTx` helper must be extended to track a separate in-memory store (e.g. `Map<cardItemId, Map<bucketId, { location, quantity }>>` for buckets) so the new helper can be exercised through the in-memory path.
4. **Hand-rolled `tx` in atomicity tests**: when a test hand-rolls a `tx` object bypassing `mockTx`, it must include every method the new helper calls. Forgetting one (e.g. `cardItemLocation`) makes the test fail with `Cannot read properties of undefined`, which looks like a production bug. Defend by including the full surface.

### 4. Run the full validation bundle, not just focused tests

The second-round correction touched mocks in 4 test files. A focused-only test run would not have caught the cross-file test-mock drift; the full `pnpm test` run did. The cost of a focused-only run is "you ship a second-round correction with 7 hidden test failures that surface on the next CI run." Always run the full bundle.

## Story artifact structure for a second-round correction

### Append, do not rewrite

A second-round Dev Agent Record section is a new "round 2" entry below the first round's section, not a rewrite of the first round. The story artifact grows; the prior round's evidence stays in place. Reviewers reading the artifact later can see what was fixed in which round and when, which is essential for audit and for the next agent's mental model.

The shape of the second-round section:

```markdown
## Dev Agent Record — YYYY-MM-DD — bmad-dev-story correction (round N)

**Trigger:** the YYYY-MM-DD fresh `bmad-code-review` returned `BLOCKED` on N new points. The
previous `bmad-dev-story` correction (commit HASH) had resolved the prior N-1 blockers; the
fresh review surfaced N more. This section records the round-N correction that resolves all N.

### Blockers fixed
1. ...
2. ...
3. ...

### Files changed (correction scope only)
...

### Validation
- prisma:validate: PASS
- typecheck: PASS
- lint: PASS
- test: N/N PASS (up from M; +K from new review-correction tests)
- build: PASS
- git diff --check: PASS

### Key decisions
- Atomicity boundary lives at the repo layer, not the action layer.
- Pre-flight invariant guard at the repo helper.
- ...

### Carry-forward (preserved from prior corrections)
- ...

### Out of scope (preserved)
- ...

### Next
- bmad-code-review for <story-id> (fresh, on the round-N implementation).
- bmad-state-check after review.
```

### State + sprint-status updates

`_bmad/state.json`:

- `workflow_status`: `implemented_not_reviewed` (after the round-N correction).
- `active_workflow`: `bmad-code-review` (the next workflow that runs against the story).
- `blockers`: `[]` (the fresh review's blockers are resolved).
- `last_review_summary`: rewritten to describe the round-N correction.
- `last_artifacts`: add the round-N file list (including the touched test files).
- `next_recommended_workflows`: `["fresh bmad-code-review for <story-id>"]`.
- `updated_at`: refresh.

`_bmad/sprint-status.yaml`:

- Story `status`: `implemented_not_reviewed`.
- Story `review_verdict`: `BLOCKED_PENDING_RE_REVIEW` (not just `BLOCKED`, which implies unresolved).
- Story `validation_summary`: refresh the test count and add a note for the round-N delta.
- Story `review_notes`: rewritten to record the round-N correction history.
- Story `next_recommended_workflow`: `["fresh bmad-code-review for <story-id>"]`.
- `carry_forward_concerns`: the round-N line replaces the prior round's "is review-blocked" line.

`CONTINUE-HERE.md`:

- Top status block: the new current workflow is `bmad-code-review` for the story; the new round-N scope is enumerated.
- "Active / Next Workflow" section: status and next-workflow pointer updated.
- "Completed Work" entry for the story: rewritten to reflect the round-N correction.

## Reference file structure for a multi-round correction

The `references/<story>-….md` file grows in the same file, not a new one. Patterns #1-#13 (first round) and #14-#20 (second round) all belong to the same story and the natural continuation anchor is the first-round reference. Do not split into `…-r1.md` and `…-r2.md` — that fragments the pattern library.

The pattern numbers continue from the highest existing number. If the first round has patterns 1-13, the second round starts at 14. The number is just a sequence index; do not renumber when appending.

## State machine for a multi-round story

```
implemented_not_reviewed (round 1 correction)
  -> review_blocked  (round 1 review returns BLOCKED)
  -> bmad-dev-story correction (round 2)
  -> implemented_not_reviewed (round 2 correction)
  -> review_blocked  (round 2 review returns BLOCKED)
  -> bmad-dev-story correction (round 3)
  -> ...
  -> pass_with_notes / pass  (some round passes)
```

There is no fixed cap on the number of rounds, but each round should be cheaper than the last (because the boundary walk + reference file make the next round's correction smaller). If a round feels as expensive as the previous, the boundary walk was probably skipped.

## Common second-round failure modes

1. **Reading the first-round Dev Agent Record as the authoritative scope.** The first-round section is the prior commit's evidence, not the current scope. The fresh review's BLOCKED section is the current scope.

2. **Fixing the fresh review's blockers one at a time without a boundary walk.** Each blocker is fixed in isolation, but the next blocker is in an adjacent path the boundary walk would have surfaced. The correction is 2-3x longer than it needs to be.

3. **Re-running focused tests only.** A second-round correction typically touches mocks in 4+ test files. The full bundle catches cross-file test-mock drift; the focused bundle does not.

4. **Rewriting the first-round Dev Agent Record.** The first round's evidence must stay in place for the audit trail. Append a "round 2" section, do not rewrite.

5. **Splitting the reference file by round.** Patterns #1-#13 and #14-#20 belong to the same story. Do not split into `…-r1.md` and `…-r2.md` — that fragments the pattern library and forces future agents to read two files for one story.

6. **Updating only `state.json` and skipping `sprint-status.yaml` + `CONTINUE-HERE.md` + the story artifact.** All three are required for the next agent to find the work. The state.json update without the other two is a half-update.

## After the second-round correction lands

Same as a first-round correction:
- `state.json`'s `blockers` is `[]`.
- `sprint-status.yaml`'s story `status` is `implemented_not_reviewed`.
- The next workflow is fresh `bmad-code-review` for the story.
- Runtime/founder QA and live migration deployment remain unverified/out of scope unless separately run.

## CardForge CF-E5-S3 second round — concrete outcome

- **+9 focused regression tests** (4 atomic create-with-initial-buckets boundary, 3 `updateQuantityForOwner` rebalance, 2 sales deduct/restore bucket alignment).
- **+3 new repo helpers** (`createManyWithInitialBucketsForOwner`, `createWithInitialBucketForOwner`, `updateQuantityForOwner`).
- **+1 sales service helper** (`adjustBucketQuantitiesForOwner`).
- **Test suite**: 361 → 370.
- **All validation gates green**: prisma:validate, typecheck, lint 0/0, test 370/370, build, git diff --check.
- **Story trajectory**: 332 (pre-S3) → 355 (S3 + cleanup correction) → 361 (S3 first-round correction) → 370 (S3 second-round correction).
- **Reference file growth**: ~300 new lines (patterns #14-#20 + meta-pattern for second-round corrections) appended to the same file, not a new one.

The next workflow is fresh `bmad-code-review for CF-E5-S3`. Runtime/founder QA and live Supabase migration deployment remain unverified/out of scope.
