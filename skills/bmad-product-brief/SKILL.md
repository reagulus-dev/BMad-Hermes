---
name: bmad-product-brief
description: Create or update a canonical product_brief artifact through guided discovery, synthesis, and review.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, analysis, product-brief, planning-input, artifacts]
    related_skills: [bmad-brainstorming, bmad-prfaq, bmad-create-prd, bmad-artifact-policy]
---

# BMad Product Brief

## When to Use

Use when the product concept is already fairly clear and the goal is to produce a concise strategic brief rather than a more adversarial PRFAQ challenge.

## Upstream Alignment

This skill ports upstream BMad product-brief creation into Hermes.
Maintain the upstream mode:
- collaborative discovery
- product-focused synthesis
- compact executive summary output
- optional analysis of supporting artifacts before drafting

## Artifact Contract

Primary output artifact:
- `product_brief`

Preferred mechanics:
1. inspect contract with `bmad_get_artifact_contract`
2. create draft from template with `bmad_create_artifact_from_template`
3. update only legal sections with `bmad_update_artifact_section`
4. validate with `bmad_validate_artifact`

## Recommended Inputs

Best upstream inputs include:
- brainstorming notes or artifact
- market/domain/technical research
- founder intent and constraints
- existing product documentation

## Execution Pattern

1. Confirm the product concept, target users, business context, and desired scope.
2. Review any upstream analysis artifacts before drafting.
3. Create or load the canonical `product_brief` artifact.
4. Drive structured discovery around:
   - problem/opportunity
   - target user and value proposition
   - differentiators
   - strategic constraints
   - success definition
5. Draft a compact but decision-useful brief.
6. Review with the user and refine weak or vague sections.
7. Validate the artifact.
8. Route forward, usually to `bmad-create-prd`.

## Guardrails

- Do not let the brief bloat into a PRD.
- Keep it strategic and legible.
- Preserve extra details in notes only if they materially help downstream planning.
- Prefer the artifact contract over ad-hoc formatting.
- Do not mirror the product brief into multiple locations. Keep exactly one canonical file and reference it from state/status docs.
- Once PRD, UX, and architecture artifacts exist, demote the product brief to a compact founder-intent note instead of maintaining it as a second active requirements source.

## Completion Standard

Complete when the `product_brief` artifact is validated and strong enough to anchor PRD creation.
