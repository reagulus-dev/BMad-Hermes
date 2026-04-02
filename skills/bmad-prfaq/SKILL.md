---
name: bmad-prfaq
description: Run the Working Backwards PRFAQ challenge and produce a canonical prfaq artifact with strong customer-first framing.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, analysis, prfaq, working-backwards, artifacts]
    related_skills: [bmad-brainstorming, bmad-product-brief, bmad-create-prd, bmad-artifact-policy]
---

# BMad PRFAQ

## When to Use

Use when the product concept needs to be pressure-tested through a customer-first Working Backwards exercise.
Choose this over a product brief when the idea is still uncertain, ambitious, or likely to benefit from harder challenge.

## Upstream Alignment

This skill ports the upstream BMad PRFAQ challenge into Hermes.
Keep the upstream stance:
- customer-first framing
- direct challenge of vague claims
- stronger scrutiny than the product brief workflow
- market and feasibility claims should be reality-grounded where possible

## Artifact Contract

Primary output artifact:
- `prfaq`

Preferred mechanics:
1. inspect contract with `bmad_get_artifact_contract`
2. create draft from template with `bmad_create_artifact_from_template`
3. evolve content using `bmad_update_artifact_section`
4. validate with `bmad_validate_artifact`

## Execution Pattern

1. Clarify the proposed product, customer, and why this workflow is being used.
2. Gather existing context:
   - brainstorming artifact
   - research notes
   - assumptions or constraints
3. Create or open the canonical `prfaq` artifact.
4. Work through the PRFAQ shape in order:
   - press release
   - customer FAQ
   - internal FAQ
   - verdict / unresolved concerns if applicable
5. Challenge weak claims directly. Help the user strengthen them rather than accepting hand-wavy language.
6. Where necessary, recommend research before finalizing unsupported market or feasibility claims.
7. Validate the artifact.
8. Route forward to `bmad-create-prd` once the concept is battle-tested enough.

## Guardrails

- Do not soften weak concepts into fake confidence.
- Do not skip customer language in favor of implementation details.
- Do not silently invent market truth.
- Keep the final artifact aligned to the contract and template.

## Completion Standard

Complete when the `prfaq` artifact is validated and captures a credible customer-first concept ready for planning.
