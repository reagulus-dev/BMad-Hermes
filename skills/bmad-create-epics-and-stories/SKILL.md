---
name: bmad-create-epics-and-stories
description: Decompose requirements and architecture into a canonical epics_and_stories artifact suitable for implementation planning.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, solutioning, epics, stories, decomposition, artifacts]
    related_skills: [bmad-create-architecture, bmad-check-implementation-readiness, bmad-dev-story]
---

# BMad Create Epics and Stories

## When to Use

Use after architecture is sufficiently stable and the work needs to be broken down into epics and implementable stories.

## Upstream Alignment

This skill ports upstream BMad epics-and-stories creation into Hermes.
Preserve the upstream intent:
- decomposition by user value
- strong linkage back to requirements and architecture
- actionable stories with acceptance criteria

## Artifact Contract

Primary output artifact:
- `epics_and_stories`

Preferred mechanics:
1. inspect contract with `bmad_get_artifact_contract`
2. create the artifact with `bmad_create_artifact_from_template`
3. update sections with `bmad_update_artifact_section`
4. validate with `bmad_validate_artifact`

## Recommended Inputs

- `prd`
- `architecture`
- `ux_design` when relevant

## Execution Pattern

1. Review the requirement and architecture anchors.
2. Create or load the canonical `epics_and_stories` artifact.
3. Decompose the solution into epics with coherent value boundaries.
4. Break each epic into stories that are:
   - implementable
   - testable
   - traceable back to requirements
   - specific enough for sprint planning
5. Ensure acceptance criteria and dependencies are explicit enough for downstream work.
6. Validate the artifact.
7. Route forward to `bmad-check-implementation-readiness`.

## Guardrails

- Do not produce placeholder stories with vague “do X” language.
- Do not detach stories from architectural reality.
- Keep story boundaries honest and implementation-relevant.

## Completion Standard

Complete when the `epics_and_stories` artifact is validated and ready for implementation-readiness review.
