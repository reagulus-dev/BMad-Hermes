---
name: bmad-create-architecture
description: Create a canonical architecture artifact that records the solution design decisions needed for consistent implementation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, solutioning, architecture, design-decisions, artifacts]
    related_skills: [bmad-create-prd, bmad-validate-prd, bmad-create-ux-design, bmad-create-epics-and-stories]
---

# BMad Create Architecture

## When to Use

Use once requirements are stable enough to make technical design decisions.
This is the main solutioning workflow for deciding how the product should be built.

## Upstream Alignment

This skill ports upstream BMad architecture creation into Hermes.
Preserve the upstream goals:
- explicit technical decisions
- consistent implementation guidance for agents
- structured decision capture instead of vague architectural prose

## Artifact Contract

Primary output artifact:
- `architecture`

Preferred mechanics:
1. inspect contract with `bmad_get_artifact_contract`
2. create the artifact with `bmad_create_artifact_from_template`
3. update sections with `bmad_update_artifact_section`
4. validate with `bmad_validate_artifact`

## Recommended Inputs

- `prd`
- `prd_validation_report`
- `ux_design` if UX matters
- any existing project context or technical constraints

## Execution Pattern

1. Confirm the solutioning scope and technical decision surface.
2. Review planning artifacts first.
3. Create or load the canonical `architecture` artifact.
4. Drive structured decision-making around:
   - system context and boundaries
   - major components and interactions
   - critical design decisions and trade-offs
   - patterns, constraints, deployment/runtime concerns
   - implementation consistency requirements
5. Capture decisions explicitly in the artifact.
6. Validate the architecture artifact.
7. Route forward to `bmad-create-epics-and-stories`.

## Guardrails

- Do not over-specify implementation tasks that belong in stories.
- Do not leave key trade-offs implicit.
- Keep the document useful for downstream decomposition and coding agents.

## Completion Standard

Complete when the `architecture` artifact is validated and sufficient to drive epics and stories creation.
