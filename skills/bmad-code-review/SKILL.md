---
name: bmad-code-review
description: Perform a structured Alice/BMad code review as a progression gate using repo truth, validation evidence, and explicit pass/fail reasoning.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, code-review, validation, quality, gatekeeping]
    related_skills: [bmad-dev-story, bmad-evidence-reporting, bmad-state-check]
---

# Alice Code Review

## When to Use

Use after a meaningful implementation change, bug fix, or story completion attempt.

## Goal

Prevent false completion by making review a real progression gate instead of a formality.

## Canonical Naming Rule

For Alice-managed live state, use `snake_case` consistently.

Preferred field names include:
- `workflow_status`
- `last_review_summary`
- `last_evidence_path`
- `last_artifacts`
- `next_recommended_workflows`
- `updated_at`

Do not continue schema drift by introducing new review-state references in camelCase.

## Review Inputs

Inspect as many of these as are available:
- the target story or fix description
- the canonical story artifact for that work when available
- changed files and diff context
- relevant tests and validation results
- `_bmad/state.json`
- evidence artifacts under `_bmad/artifacts/evidence/`
- prior review, QA, or handoff artifacts
- runtime verification notes when the change affects real user flows

## Review Dimensions

Check for:
- correctness relative to the requested change
- obvious regressions or edge cases
- missing validation
- maintainability or clarity problems that materially affect trust
- mismatch between claim and evidence
- stale or inaccurate workflow state
- missing acknowledgment of unverified runtime areas

## Review Procedure

1. Confirm the review target.
2. Read current `_bmad/state.json`.
3. Inspect code changes and surrounding context.
4. Inspect test, build, and runtime evidence.
5. Identify blocking vs non-blocking findings.
6. Produce a clear verdict.
7. If blocked, route back to correction work rather than pretending the story is done.

## Verdicts

Use one of:
- PASS
- PASS WITH NOTES
- BLOCKED

### PASS

Use only when the implementation and available evidence support progression.

### PASS WITH NOTES

Use when no blocker exists but there are still minor concerns or explicit unverified areas.

### BLOCKED

Use when correctness, risk, or missing evidence prevents progression.

## Important Scope Rule

A review verdict governs code-review progression only.

A `PASS` or `PASS WITH NOTES` is not by itself:
- a QA pass
- founder-review readiness
- release readiness

Runtime-sensitive readiness must be decided separately through the QA gate and accompanying evidence.

## Output Format

Include:
- Review target
- Evidence inspected
- Findings
- Verdict
- Required next action

Prefer evidence-inspected details such as:
- exact validation commands reviewed
- exact runtime checks reviewed or missing
- exact artifacts inspected
- explicit unverified areas

## Rules

- Do not confuse a clean diff with a validated change.
- Do not pass work that lacks necessary evidence for its risk level.
- Do not bury blockers in soft language.
- Do not mark runtime-sensitive changes complete without acknowledging runtime verification gaps.
- Do not treat generated tests or nominal QA workflow completion as founder-review readiness by themselves.
- For story-scoped work, prefer appending review findings to the relevant story or review thread instead of creating detached duplicate summaries.

## Artifact Anchor Rule

For story-scoped work, always append findings to the `## Review Findings` section of the story artifact.
Do not create a separate review file for story-scoped work.
Create a standalone review artifact only when the review is cross-story, release-wide, or too large to fit in the story thread.

## State Handling

After review, ensure `_bmad/state.json` reflects reality:
- `workflow_status` should align with the real progression state
- `last_review_summary` should be updated
- `next_recommended_workflows` should be explicit
- `last_artifacts` should include the most relevant touched review or story anchor when appropriate
- `updated_at` should be refreshed

Do not set a completion-like state solely because review passed.

## Completion Standard

A good review gives a trustworthy verdict and a clear next move.
For app or product work, founder-review readiness requires more than a clean code review: it requires runtime evidence or an explicit statement that runtime verification is still missing.
