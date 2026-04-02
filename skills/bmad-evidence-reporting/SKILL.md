---
name: bmad-evidence-reporting
description: Standardize BMad completion reporting with explicit evidence blocks, honest status labels, and project-local evidence artifacts under `_bmad/`.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, evidence, reporting, validation, qa]
    related_skills: [bmad-dev-story, bmad-code-review, bmad-state-check]
---

# BMad Evidence Reporting

## When to Use

Use whenever reporting that work is fixed, done, ready for QA, ready for handoff, or otherwise operationally meaningful.

## Goal

Make completion claims trustworthy, repeatable, and traceable to project-local evidence.

## Canonical Naming Rule

For BMad-managed live state, use `snake_case` consistently.

Preferred state fields to update or reference include:
- `last_evidence_path`
- `last_artifacts`
- `last_review_summary`
- `workflow_status`
- `updated_at`

Do not introduce new live-state evidence references in mixed camelCase.

## Minimum Evidence Block

Every meaningful completion or update claim should include:
- Change target
- Validation command(s)
- Runtime verification
- Result
- Unverified

## Status Taxonomy

Prefer these labels when evidence is partial:
- implemented, not yet reviewed
- reviewed, not yet runtime-verified
- build-passing, runtime-unverified
- blocked
- complete with evidence

## Reporting Rules

- If runtime truth is missing, say so explicitly.
- If review is missing, say so explicitly.
- If validation was narrow, say what was and was not covered.
- If there are blockers, do not soften them into optimistic language.
- Do not equate test generation or passing automated tests alone with founder-review readiness for usability-sensitive app flows.

## Example Structure

```text
Change target: settings save flow for profile screen
Validation command(s): npm test -- profile-settings ; npm run build
Runtime verification: manually exercised save + reload flow in local app session
Result: PASS
Unverified: no mobile-device verification yet; no network-loss scenario tested
```

## Artifact Routing Rule

When evidence belongs to story-linked work:
- prefer updating the existing story thread first
- if needed, append to the linked review or QA thread
- create a standalone evidence file only when the evidence is substantial, cross-cutting, or awkward to keep inside the story thread

The goal is traceability without artifact sprawl.

## Canonical Evidence Location

When a standalone evidence artifact is warranted, save it under:
- `_bmad/artifacts/evidence/`

Suggested naming:
- `YYYY-MM-DD-short-topic.md`

## QA and Review Alignment

Evidence reporting should support later review and QA gating.
A good evidence report makes it obvious:
- what changed
- what was validated
- what runtime verification happened
- what remains unverified
- what gate claims are still premature

## State Update Guidance

After producing meaningful evidence, ensure `_bmad/state.json` reflects reality:
- `last_evidence_path` should point to the strongest relevant evidence artifact when one exists
- `last_artifacts` should include the most relevant story, review, QA, or evidence anchors
- `updated_at` should be refreshed
- `workflow_status` should not be upgraded beyond what the evidence truly supports

Do not imply completion through state changes if runtime evidence is still missing.

## Bad Patterns to Avoid

Do not say:
- `done` with no commands
- `fixed` with no observed result
- `ready for QA` when no evidence was gathered
- `works` when runtime was not exercised
- `founder-review ready` based only on tests or code review

## Completion Standard

A good evidence report narrows uncertainty instead of hiding it.
