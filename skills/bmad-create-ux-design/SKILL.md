---
name: bmad-create-ux-design
description: Create a canonical ux_design artifact that translates product requirements into a structured experience design specification.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, planning, ux, design, artifacts]
    related_skills: [bmad-create-prd, bmad-validate-prd, bmad-create-architecture]
---

# BMad Create UX Design

## When to Use

Use when user experience is a meaningful part of the product and the team needs a structured UX specification before implementation.

## Upstream Alignment

This skill ports upstream BMad UX design creation into Hermes.
Preserve the upstream collaborative mode:
- visual/experience discovery
- user journey clarity
- design principles and patterns
- structured specification rather than aesthetic improvisation

## Artifact Contract

Primary output artifact:
- `ux_design`

Preferred mechanics:
1. inspect contract with `bmad_get_artifact_contract`
2. create or load the artifact with `bmad_create_artifact_from_template`
3. update sections with `bmad_update_artifact_section`
4. validate with `bmad_validate_artifact`

## Recommended Inputs

- validated `prd`
- product brief or PRFAQ if relevant
- any design references, brand rules, accessibility constraints, or example apps

## Execution Pattern

1. Confirm whether UX work is required and what surface area it covers.
2. Review the PRD and any existing constraints.
3. Create or open the canonical `ux_design` artifact.
4. Drive structured design discovery around:
   - experience goals
   - users and primary journeys
   - interaction patterns
   - responsiveness and accessibility
   - component/system considerations
5. Capture decisions in the contract-backed artifact.
6. Validate the artifact.
7. Route forward to architecture and implementation-readiness workflows.

## Guardrails

- Do not confuse UX spec with UI mockups unless the artifact contract requires visual detail.
- Keep the document actionable for downstream agents.
- Preserve accessibility and responsive behavior as first-class concerns.

## Completion Standard

Complete when the `ux_design` artifact is validated and usable by architecture and implementation planning.
