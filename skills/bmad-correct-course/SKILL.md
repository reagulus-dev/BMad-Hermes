---
name: bmad-correct-course
description: Correct course when implementation, validation, review, QA, or state reality diverges from the current story or plan. Use to turn surprises into explicit correction work instead of vague optimism.
version: 2.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, correction, triage, replanning, blockers, recovery]
    related_skills: [bmad-state-check, bmad-dev-story, bmad-code-review, bmad-qa-gate, bmad-artifact-policy]
---

# BMad Correct Course

Correct course when implementation, validation, review, QA, or state reality diverges from the current story or plan. Use to turn surprises into explicit correction work instead of vague optimism.

## When to Use

Use when current work can no longer honestly proceed under the original story, validation claim, review result, or workflow assumption.

Typical triggers:
- validation fails in a non-trivial way
- the bug was not actually fixed
- the issue cannot be reproduced as originally described
- review or QA finds blocking problems
- runtime behavior contradicts the story's implied acceptance
- repo reality and `_bmad/state.json` materially disagree
- scope expands beyond the original story boundaries
- a release or founder-review claim is no longer supportable
- a documented "preserve legacy" scope item was a defensive default that no longer matches the project context (e.g. solo founder, pre-launch)

## Goal

Turn drift, failure, or surprise into an explicit correction workflow with a traceable artifact, updated state, and a justified next move.

## Core Principle

Do not hide course correction inside soft language.

When the plan is wrong, say it.
When the story is insufficient, say it.
When the evidence is weak, say it.
Then route the work explicitly.

## Canonical Naming Rule

For BMad-managed live state, use `snake_case` consistently.

Preferred fields include:
- `workflow_status`
- `current_story`
- `current_epic`
- `current_sprint`
- `blockers`
- `last_artifacts`
- `last_review_summary`
- `last_evidence_path`
- `next_recommended_workflows`
- `updated_at`
- `state_check`

Do not introduce new correction state using mixed camelCase names.

## Inputs to Inspect

Inspect as many of these as are available:
- `_bmad/state.json`
- the target story or fix artifact
- the relevant review artifact
- the relevant QA or evidence artifact
- failing validation results
- repo truth such as changed files, tests, logs, and runtime observations
- recent legacy artifacts if the project still relies on `_bmad-output/`

## Correction Procedure

1. Confirm the failing or diverging target.
2. State exactly what assumption broke.
3. Identify whether the problem is:
   - implementation defect
   - misunderstood requirements
   - missing context in the story
   - bad workflow state
   - insufficient evidence
   - genuine scope change
4. Decide the correction scope:
   - same story, continue with correction
   - same story, but blocked pending new information
   - route back to implementation
   - route back to review
   - route back to QA
   - route back to planning or story shaping
5. Append findings to the canonical story, review, or QA thread when possible.
6. Create a standalone correction artifact only when the issue is cross-story, release-wide, or too large for the story thread.
7. Update `_bmad/state.json` honestly.
8. Make `next_recommended_workflows` explicit.

## Required Output Block

Always include:
- Correction target
- Broken assumption
- Evidence observed
- Impacted scope
- Recommended route
- Blockers
- Unverified

## Artifact Routing Rule

Prefer this anchor order:
1. existing story artifact
2. existing review artifact for that story
3. existing QA artifact for that story or release thread
4. standalone correction artifact under `_bmad/artifacts/corrections/` if the issue is cross-cutting or too large for a story thread

Suggested standalone correction naming:
- `_bmad/artifacts/corrections/YYYY-MM-DD-topic.md`

## State Update Rules

After correction triage, update `_bmad/state.json` to reflect reality:
- `workflow_status` should become `blocked`, `in_progress`, or another honest non-complete state as appropriate
- `current_story` should remain set if the correction is still story-scoped
- `blockers` should list explicit blockers, not vague concern language
- `last_artifacts` should include the touched story, review, QA, or correction artifacts
- `last_review_summary` should be updated if review findings materially changed the route
- `last_evidence_path` should be updated if new evidence changed the diagnosis
- `next_recommended_workflows` should clearly say what comes next
- `updated_at` should be refreshed

## Decision Rules

- If the problem is still within the same story scope, prefer correcting within that story instead of spawning unnecessary new stories.
- When review finds blockers but the acceptance criteria and story shape remain valid, use `bmad-correct-course` as triage only and route the same story back to `bmad-dev-story` correction; do not create a standalone correction artifact unless the issue is cross-story or changes the plan/story contract.
- If the story no longer honestly contains the work, say so explicitly and route back to planning or story shaping.
- If QA disproves readiness, downgrade the claim immediately.
- If runtime evidence contradicts test results, trust runtime reality.
- If state and repo disagree, report the disagreement instead of choosing the more optimistic side.

## Bad Patterns to Avoid

Do not:
- relabel a blocker as a note
- keep a completion claim alive after contradictory evidence
- spawn new documents for every small correction when the story thread already exists
- pretend scope drift is just implementation delay
- update code without updating state and artifact truth

## Pre-Existing "Preserve Legacy" Choices Often Deserve Reversal

Many stories include a defensive scope item like "preserve the existing `X` column for backward compatibility" or "keep both the new and the old field in sync." That is the right default for a multi-tenant production app with live users. It is the **wrong** default when:

- the founder is the only test user (no migration to defend against),
- no production data exists yet (the existing column has no real semantics in production),
- the dual-write path adds measurable complexity (two write paths, two read branches, a search-filter OR clause, a UI fallback).

When the user later asks "would it be cleaner to remove the legacy code?", the answer is usually yes. Encode this as a correction with these properties:

- **Mid-story scope refinement, not a new story.** Open the story artifact and **amend it first** with a clearly-labeled "Cleanup Correction" section that supersedes the original scope item. The amendment is the canonical record of what changed. Do not start editing code until the story artifact is updated.
- **Update the artifact first, code second.** The user explicitly said "Update the story before starting so that we avoid confusion." When a correction supersedes a documented scope decision, the story artifact amendment is the authoritative proof that the original decision was revised; later agents reading the artifact will not be confused by a "scope item" that the implementation does not honor.
- **One cleanup migration, not a squash.** Add a new migration (`<timestamp>_<verb>_<noun>` such as `20260602000001_drop_card_item_location_legacy`) that performs the destructive change. Do not edit the original additive migration in place — that would corrupt migration history for any database that already ran it.
- **Tests assert the absence.** Schema integrity tests should include a positive assertion that the cleanup migration drops the legacy column, and a negative assertion that the schema no longer carries the legacy field. Tests updated in place to drop the legacy field from fixture payloads are part of the same commit, not a follow-up.
- **Carry-forward note: do not reintroduce.** Add an explicit carry-forward line in `sprint-status.yaml` and `state.json` saying "do not reintroduce the legacy `X` column; if a new use case needs a similar free-text, it should live on `CardItem` as a different field (e.g. `displayLabel`) and not be confused with the per-bucket model field." Future agents reading the carry-forward know not to add it back.

## When to Use vs. When to Defer to bmad-feature-retirement-clean-removal

`bmad-correct-course` handles in-flight corrections within an active story or sprint. `bmad-feature-retirement-clean-removal` handles a multi-step retirement of a user-facing feature after the story is closed (delete code, update user-facing copy, verify the app still installs). The dividing line:

- Correction in this skill: the work is scoped inside an active story; the story artifact is the anchor; one or two commits; same validation gates; the next workflow after correction is `bmad-code-review` for the same story.
- Feature retirement in the other skill: the feature is already shipped (or partially shipped), no active story owns the removal, the work touches user-facing copy/routes/installer, and the goal is to ship a "feature is gone" release.

**Removing a single data field inside an active story is a correction, not a feature retirement.** Even if the field is a back-compat column, removing it does not change user-visible behavior (the user already had to be on the new code path to interact with the data model), so it does not need the multi-step retirement ceremony.

## Production Regression Discovered After a Story Closed → New Story, Not Correction

When a runtime regression surfaces in production against a story that already has `status: completed` and a code-review verdict (e.g. `PASS_WITH_NOTES`), **do NOT reopen the closed story as a correction**. Open a new story. This is a BMad discipline rule, not a preference:

- A closed story is the unit of completed work. Reopening it as a "correction" silently revises the original completion claim and corrupts the review trail.
- The new regression is a new piece of work with its own scope, its own acceptance criteria, its own validation gates, and its own code-review verdict. Trying to fold it into the closed story either buries the new evidence under the old story's history or forces the story to be re-reviewed end-to-end.
- The new story gets its own story artifact at `_bmad/artifacts/stories/<EPIC>-S<n>-<slug>.md`, its own sprint-status entry, and its own `next_recommended_workflow: bmad-dev-story`.

**Concrete signal pattern (the "P2028 on a closed story" case):**

1. The user reports a runtime error that can be reproduced in production.
2. Git history shows the affected code was introduced in a story that already closed (e.g. CF-E5-S3) and was not regressed by any later story.
3. The E2E suite of the closed story was a "smoke" (read paths, dialog reachability) and never exercised the failing write path.
4. The user's first instinct is "this was working before" — they may even be right, in the sense that the *unit tests* and the *smoke* were green. The failing path was always latent against the live pooler / live env.

**The right move in this case is:**

1. Use `bmad-state-check` to confirm the previously-closed story is genuinely closed (not a stale-state artifact) and to identify the active story.
2. Open a new story via `bmad-create-story` with a clear scope: "Restore $transaction on production by routing it to the direct-connection client." The story artifact must record the root cause (history-check evidence: which story introduced the failing code path, which test suite never exercised it) so the next session can see the chain of reasoning without re-deriving it.
3. The new story's `selection_notes` must explicitly say "selected after founder reported P2028 on live production CSV import; previous story CF-E5-S4 was the most recent deploy but did not introduce the bug; CF-E5-S3 introduced the $transaction call site against a test DB; CF-E5-S4 smoke never exercised it." That way `bmad-state-check` in the next session can recover the chain.
4. Implement the fix in `bmad-dev-story`, run the same validation gates, and run `bmad-code-review` on the new diff. The closed story stays closed; the new story gets its own PASS_WITH_NOTES verdict.
5. Update `sprint-status.yaml` with the new epic entry (or add to the current epic if the regression is in-scope for the epic), and update `CONTINUE-HERE.md` with the regression date, root cause, fix, and evidence. The carry-forward section in `sprint-status.yaml` should also gain a line so future agents know not to undo the fix.

**The wrong move in this case:**

- Reopen CF-E5-S4 with a "correction" entry that adds the regression fix scope to the closed story. This makes the closed story "completed + correction + correction + correction" with no clear unit of work, breaks the review trail, and forces any future agent reading the artifact to reconstruct which scope is the original completion and which is the regression fix.
- Quietly land the fix in a single commit titled "fix: csv import" without opening a story. This makes the regression invisible in BMad state and guarantees the next session will not know it was a regression, what the root cause was, or why the dual-client pattern was added.

**The dividing line between "in-story correction" and "new story"**: if the regression can be fixed by changing code that was introduced in the current active story, it is a correction. If the regression is in code that was introduced in a closed story, the regression is its own new piece of work.

## Completion Standard

A good correction workflow turns confusion into a traceable diagnosis, an honest state update, and a justified next move.
