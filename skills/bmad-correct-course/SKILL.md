---
name: bmad-correct-course
description: Correct course when implementation, validation, review, QA, or state reality diverges from the current story or plan. Use to turn surprises into explicit correction work instead of vague optimism.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, correction, triage, replanning, blockers, recovery]
    related_skills: [bmad-state-check, bmad-dev-story, bmad-code-review, bmad-qa-gate, bmad-artifact-policy]
---

# BMad Correct Course

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

## Completion Standard

A good correction workflow turns confusion into a traceable diagnosis, an honest state update, and a justified next move.
