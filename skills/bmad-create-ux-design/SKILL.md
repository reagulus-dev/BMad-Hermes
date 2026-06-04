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
- competitor/public-product references when the user asks to take inspiration from another product or established tool category
- for brownfield refreshes: current repo reality, current screen/component inventory, and any continuation docs that describe the latest known state

## Reference Packs

- `references/checkout-bot-operator-console-patterns.md` — concise reusable notes for checkout-bot/operator-console UX research such as task groups, profile/session separation, route/proxy groups, verification queues, Discord alerts, row actions, and early cart/price guardrail placement.

## Execution Pattern

1. Confirm whether UX work is required and what surface area it covers.
2. Review the PRD and any existing constraints.
3. If the request is a brownfield UI refresh or reboot, do a lightweight reality-first audit before drafting recommendations:
   - inspect project state and continuation docs
   - audit the current UI architecture in code, especially screen scaffolds, safe-area handling, keyboard avoidance, modal/sheet patterns, primitive reuse, and theme/token drift
   - where helpful, parallelize web research and code audit with isolated subagents so implementation evidence and external design guidance arrive independently
4. Create or open the canonical `ux_design` artifact.
5. If the user names a reference product or tool class, run a lightweight public-source UX scan before tightening the artifact:
   - inspect the reference product’s public docs/site/screens where available
   - extract reusable IA/setup patterns, not copy or confidential implementation details
   - save concise notes under the project’s planning artifacts when they materially shape the UX
   - distinguish patterns to borrow from patterns intentionally not borrowed
6. Drive structured design discovery around:
   - experience goals
   - users and primary journeys
   - interaction patterns
   - responsiveness and accessibility
   - component/system considerations
   - for brownfield mobile apps: layout foundation, keyboard behavior, safe areas, and presentation taxonomy before cosmetic polish
   - safety-critical workflow ordering, especially when UX decisions affect when irreversible or high-risk actions happen
7. When founder feedback changes workflow ordering or product invariants, reconcile every upstream/downstream artifact that would otherwise drift: UX, PRD, architecture, product brief, continuation docs, and live BMad state.
8. Capture decisions in the contract-backed artifact.
9. Validate the artifact.
10. Route forward to architecture and implementation-readiness workflows.

## Guardrails

- Do not confuse UX spec with UI mockups unless the artifact contract requires visual detail.
- Keep the document actionable for downstream agents.
- Preserve accessibility and responsive behavior as first-class concerns.
- When borrowing from competitors or category leaders, borrow workflow structure and operator affordances, not brand/confidential details; cite the public source class in project-local research notes.
- For guardrail-sensitive products, do not bury safety checks late in the UI flow. Place them at the earliest reliable checkpoint and explicitly show later re-checks before irreversible actions.
- For brownfield mobile redesigns, do not jump straight to aesthetics. If the repo shows structural UI issues, recommend a foundation-first plan: primitives/scaffolds, safe-area normalization, keyboard-safe forms, and modal/sheet standardization before broad visual restyling.
- When recommending glassmorphism or other premium visual directions, treat them as restrained chrome-layer choices, not a reason to blur every surface.
## Completion Standard

Complete when the `ux_design` artifact is validated and usable by architecture and implementation planning.
