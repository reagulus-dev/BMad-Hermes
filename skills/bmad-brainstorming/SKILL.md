---
name: bmad-brainstorming
description: Facilitate structured brainstorming and capture the output into the canonical brainstorming_session artifact for downstream BMad workflows.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, analysis, brainstorming, ideation, artifacts]
    related_skills: [bmad-product-brief, bmad-prfaq, bmad-state-check, bmad-artifact-policy]
---

# BMad Brainstorming

## When to Use

Use when the user wants to ideate before committing to a brief, PRFAQ, PRD, or architecture direction.

This is the Phase 1 exploratory workflow that should produce a canonical `brainstorming_session` artifact rather than freeform notes.

## Upstream Alignment

This skill ports the upstream BMad brainstorming workflow into Hermes.
Keep the upstream spirit:
- interactive facilitation
- divergent thinking before convergence
- multiple ideation techniques
- delayed organization until enough ideas exist

Do not reduce this to a quick bullet list.

## Artifact Contract

Primary output artifact:
- `brainstorming_session`

Preferred mechanics:
1. inspect the contract with `bmad_get_artifact_contract`
2. create the artifact from template with `bmad_create_artifact_from_template`
3. evolve the content using `bmad_update_artifact_section`
4. validate with `bmad_validate_artifact`

Do not draft the final brainstorming artifact freehand if the tool path is available.

## Execution Pattern

1. Clarify the idea space, target domain, and what kind of thinking is needed.
2. Ask whether there is existing context to consider:
   - existing notes
   - product concept
   - market assumptions
   - technical constraints
3. Create or locate the canonical brainstorming artifact.
4. Facilitate ideation in rounds. Intentionally vary technique and perspective:
   - user problems and JTBD
   - customer segments
   - differentiators
   - business model
   - technical opportunities
   - risks and edge cases
5. Push past the obvious ideas before organizing.
6. Converge into themes, opportunities, open questions, and candidate next directions.
7. Validate the artifact and explicitly recommend the next workflow:
   - `bmad-product-brief`
   - `bmad-prfaq`
   - occasionally direct research workflows if uncertainty remains high

## Interaction Rules

- Prefer interactive facilitation over silent drafting.
- If the user already provided a large idea dump, synthesize it into the artifact rather than re-asking everything.
- Keep idea generation broad before evaluating.
- Do not pretend brainstorming has produced commitments that belong in later artifacts.

## Completion Standard

Complete when the brainstorming artifact is populated, validated, and usable as structured input for `bmad-product-brief` or `bmad-prfaq`.
