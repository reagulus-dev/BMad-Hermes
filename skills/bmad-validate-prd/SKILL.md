---
name: bmad-validate-prd
description: Validate a PRD against BMad planning standards and produce a canonical prd_validation_report artifact.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, planning, prd-validation, quality-gate, artifacts]
    related_skills: [bmad-create-prd, bmad-create-ux-design, bmad-create-architecture]
---

# BMad Validate PRD

## When to Use

Use after PRD drafting and before deeper solutioning.
This is the quality gate that checks whether the PRD is complete, coherent, measurable, and ready to drive UX and architecture work.

## Artifact Contracts

Primary input artifact:
- `prd`

Primary output artifact:
- `prd_validation_report`

Preferred mechanics:
1. read and validate the PRD with `bmad_read_artifact` / `bmad_validate_artifact`
2. create the validation report with `bmad_create_artifact_from_template`
3. update sections with `bmad_update_artifact_section`
4. validate the report itself with `bmad_validate_artifact`

## Upstream Alignment

This skill ports upstream BMad PRD validation into Hermes.
Keep the upstream validation mindset:
- density and completeness checks
- traceability and coverage checks
- measurability and readiness checks
- explicit report output rather than informal comments

## Execution Pattern

1. Load the canonical PRD artifact.
2. Check the PRD structurally first.
3. Review for quality dimensions such as:
   - scope clarity
   - requirement measurability
   - missing assumptions or ambiguity
   - implementation leakage
   - gaps between vision and requirements
   - readiness for UX and architecture
4. Create or update the canonical `prd_validation_report` artifact.
5. Record explicit findings, strengths, issues, and recommended corrections.
6. Validate the report artifact.
7. Route next:
   - back to PRD editing if blocked
   - forward to `bmad-create-ux-design` and/or `bmad-create-architecture` if acceptable

## Guardrails

- Do not silently “fix” the PRD during validation.
- Distinguish validation findings from edits.
- Be explicit about what blocks downstream work vs what is only a note.

## Completion Standard

Complete when the `prd_validation_report` artifact is validated and gives an honest go/no-go signal for solutioning.
