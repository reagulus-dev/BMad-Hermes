---
name: bmad-qa-gate
description: Strengthen QA/release gating for BMad. Distinguishes test generation from true founder-review readiness and requires runtime evidence for usability-sensitive app flows.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, qa, release, gating, validation, founder-review]
    related_skills: [bmad-code-review, bmad-evidence-reporting, bmad-artifact-policy, bmad-dev-story]
---

# BMad QA Gate

## Goal

Prevent false QA passes and false `ready for founder review` claims.

## Canonical Naming Rule

For BMad-managed live state, use `snake_case` consistently.

Preferred field names include:
- `workflow_status`
- `last_review_summary`
- `last_evidence_path`
- `last_artifacts`
- `next_recommended_workflows`
- `updated_at`

Do not continue schema drift by introducing new gate-related state references in camelCase.

## Important Distinction

Test automation generation is NOT the same as QA signoff.
Passing tests is NOT the same as app usability.
Code review is NOT the same as runtime validation.

## Use When

Use before saying any of the following:
- ready for QA
- QA passed
- ready for founder review
- founder review ready
- ready for release
- app is done

## Required Evidence Classes

### 1. Implementation evidence
- target story or fix identified
- changed files known
- build, test, or static validation results recorded

### 2. Review evidence
- code review performed
- blocking findings resolved or explicitly listed

### 3. Runtime evidence
For usability-sensitive flows, require real runtime evidence such as:
- manual testing on the actual build or device
- end-to-end execution on the actual app path
- screenshot, video, or log evidence where useful

Usability-sensitive flows include:
- auth
- onboarding
- navigation
- payments or subscriptions
- forms and save flows
- notifications
- household or shared-state flows
- scanner or camera flows
- anything the founder will directly judge as core app usability

## Founder Review Gate

Do NOT say founder-review ready unless all are true:
- the scoped change or story is identified
- code review is complete or explicitly waived with reason
- runtime verification happened on the relevant app surface or build
- known bugs affecting the scoped area are listed
- remaining unverified areas are explicitly listed

## Verdict Labels

Use one of:
- test-generated only
- code-reviewed, runtime-unverified
- runtime-verified for scoped flow
- founder-review ready for scoped flow
- blocked

If runtime evidence is absent, the strongest allowed verdict for usability-sensitive work is:
- `code-reviewed, runtime-unverified`

## Required Output Block

Always include:
- Change target
- Validation command(s)
- Runtime verification
- Result
- Unverified
- Gate verdict

## Artifact Routing Rule

For story-linked work, always append findings to the `## QA Findings` section of the story artifact.
Do not create a separate QA file for story-scoped work.
Create a standalone QA artifact under `_bmad/artifacts/qa/` only when findings are cross-story, release-wide, or too large to fit in the story thread.

## State Handling

After applying the QA gate, ensure `_bmad/state.json` reflects reality:
- `workflow_status` should not be upgraded beyond what the evidence truly supports
- `last_review_summary` and `last_evidence_path` should already exist or their absence should be called out explicitly as a gap
- `last_artifacts` should include the most relevant story, QA, review, or evidence anchors
- `next_recommended_workflows` should be explicit
- `updated_at` should be refreshed

Do not set a completion-like state based on test generation alone.

## Manual QA Feedback Loop

When manual testing finds bugs after a nominal pass:
1. treat that as evidence the gate was too weak
2. route the issue into `bmad-correct-course`, `bmad-dev-story`, or `bmad-code-review` as appropriate
3. append findings to the relevant story or QA thread
4. patch the relevant BMad skill if the process gap is reusable

## YOLO Mode Policy

Autonomous or YOLO implementation is allowed.
Autonomous completion claims are not allowed to outrun evidence.
The stronger the autonomy, the stricter the gate must be.

## Completion Standard

A good QA gate prevents unusable software from being presented as ready.
