---
name: bmad-create-prd
description: Create a canonical PRD artifact through disciplined stepwise discovery, decomposition, and validation-ready writing.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, planning, prd, requirements, artifacts]
    related_skills: [bmad-product-brief, bmad-prfaq, bmad-validate-prd, bmad-create-ux-design, bmad-create-architecture]
---

# BMad Create PRD

## When to Use

Use when the product concept is ready to be translated into a structured Product Requirements Document.
Typical predecessors are `bmad-product-brief` or `bmad-prfaq`.

## Upstream Alignment

This skill ports the upstream BMad PRD creation workflow into Hermes.
Preserve the upstream discipline:
- stepwise progression
- requirements-first thinking
- no skipping to implementation details
- explicit success criteria, user journeys, functional and non-functional requirements

## Artifact Contract

Primary output artifact:
- `prd`

Preferred mechanics:
1. inspect contract with `bmad_get_artifact_contract`
2. create the artifact from template with `bmad_create_artifact_from_template`
3. update sections incrementally with `bmad_update_artifact_section`
4. validate with `bmad_validate_artifact`

## Recommended Inputs

Use any of the following if available:
- `product_brief`
- `prfaq`
- brainstorming outputs
- research notes
- founder constraints

## Execution Pattern

1. Confirm which upstream artifact anchors the PRD.
2. Create or load the canonical `prd` artifact.
3. Drive discovery and drafting in a disciplined sequence:
   - problem / vision framing
   - executive summary / context
   - success metrics
   - user journeys
   - scope and boundaries
   - functional requirements
   - non-functional requirements
4. Keep implementation choices out unless the contract explicitly allows them.
5. Ask for clarification where ambiguity would cause downstream decomposition failure.
6. Validate the PRD.
7. Route next to `bmad-validate-prd`, then to UX/architecture as appropriate.

## Guardrails

- Do not turn the PRD into architecture.
- Do not write vague requirements that cannot be checked later.
- Prefer measurable success language where possible.
- Preserve contract structure so validation and downstream solutioning remain deterministic.

## Completion Standard

Complete when the `prd` artifact is validated and strong enough for PRD validation and solutioning workflows.
