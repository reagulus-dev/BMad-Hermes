---
name: bmad-check-implementation-readiness
description: Validate that planning and solutioning artifacts are complete and aligned before Phase 4 implementation starts.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, solutioning, readiness, quality-gate, artifacts]
    related_skills: [bmad-create-prd, bmad-validate-prd, bmad-create-architecture, bmad-create-epics-and-stories, bmad-sprint-planning]
---

# BMad Check Implementation Readiness

## When to Use

Use after PRD, architecture, and epics/stories exist and before Phase 4 implementation begins.
This is the cross-artifact gate that checks whether planning is actually good enough to hand to implementation.

## Upstream Alignment

This skill ports upstream BMad implementation-readiness checking into Hermes.
Preserve the upstream mindset:
- traceability review
- cross-artifact alignment
- honest readiness verdicts
- explicit report output instead of vague reassurance

## Primary Inputs

Review these artifacts where available:
- `prd`
- `prd_validation_report`
- `ux_design`
- `architecture`
- `epics_and_stories`

## Output Artifact

Current plugin registry does not yet define a dedicated `readiness_report` artifact contract.
Until one exists, anchor findings in the most appropriate existing planning artifact or create a documented structured note only if necessary.
If a readiness artifact contract is later added, migrate this workflow to use it mechanically.

## Execution Pattern

1. Load and inspect the planning and solutioning artifacts.
2. Check for cross-artifact consistency:
   - PRD ↔ architecture
   - PRD ↔ epics/stories
   - UX ↔ PRD/architecture when relevant
3. Identify missing requirements coverage, vague stories, architectural mismatches, or unresolved blockers.
4. Produce an explicit readiness verdict:
   - PASS
   - CONCERNS
   - FAIL / BLOCKED
5. Record findings in a structured, auditable way.
6. Recommend the next step:
   - `bmad-sprint-planning` if ready
   - correction of PRD / architecture / epics-and-stories if not

## Guardrails

- Do not greenlight implementation just because artifacts exist.
- Be explicit about unresolved gaps.
- Keep the verdict bounded by evidence.

## Completion Standard

Complete when there is an honest readiness assessment tying together all relevant artifacts and a clear next workflow recommendation.
