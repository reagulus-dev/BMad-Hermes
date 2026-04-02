---
name: bmad-generate-project-context
description: Generate a canonical project_context artifact that captures the implementation rules, patterns, and constraints AI agents should follow across the project.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, solutioning, project-context, agent-guidance, artifacts]
    related_skills: [bmad-create-architecture, bmad-check-implementation-readiness, bmad-operating-model]
---

# BMad Generate Project Context

## When to Use

Use when the project needs a compact, high-signal context artifact that teaches future coding agents the non-obvious implementation rules they must follow.

Typical uses:
- after architecture is stable enough to summarize conventions
- in brownfield projects where codebase norms must be captured
- before implementation if agent consistency matters

## Upstream Alignment

This skill ports upstream BMad project-context generation into Hermes.
Preserve the upstream intent:
- concise, LLM-oriented guidance
- focus on non-obvious rules, patterns, and constraints
- avoid bloated documentation dumps
- optimize for future agent consistency

## Artifact Contract

Primary output artifact:
- `project_context`

Preferred mechanics:
1. inspect contract with `bmad_get_artifact_contract`
2. create the artifact from template with `bmad_create_artifact_from_template`
3. update sections with `bmad_update_artifact_section`
4. validate with `bmad_validate_artifact`

## Recommended Inputs

Use the strongest available sources:
- `architecture`
- `prd`
- `ux_design` if relevant
- real codebase conventions from the repository
- deployment/runtime constraints
- user-specific standards and project rules

## Execution Pattern

1. Determine whether this is greenfield or brownfield.
2. Review architecture and any existing implementation guidance.
3. Inspect the codebase for conventions that would be easy for future agents to miss.
4. Create or load the canonical `project_context` artifact.
5. Capture only the highest-value rules, such as:
   - architecture boundaries and layering rules
   - framework or library conventions
   - testing expectations
   - deployment/runtime constraints
   - naming or folder conventions
   - patterns to copy and anti-patterns to avoid
6. Keep the artifact lean and future-agent-oriented.
7. Validate the artifact.
8. Route forward to implementation planning or story execution.

## Guardrails

- Do not dump the whole codebase into the artifact.
- Do not restate obvious or generic programming advice.
- Prefer project-specific guidance that reduces future agent errors.
- Keep the document contract-backed and auditable.

## Completion Standard

Complete when the `project_context` artifact is validated and useful as a compact constitution for future BMad implementation work.
