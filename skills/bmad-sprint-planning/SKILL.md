---
name: bmad-sprint-planning
description: Initialize or update sprint-status tracking for the next implementation cycle using the BMad tool/plugin layer and project-local state.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, sprint-planning, implementation, state]
    related_skills: [bmad-project-init, bmad-state-check, bmad-create-story]
---

# BMad Sprint Planning

## When to Use

Use when implementation planning is complete and the project needs a canonical `sprint-status.yaml` to sequence work.

## Goal

Create or refresh sprint tracking in a structured way so the next workflow can be routed mechanically.

## Rules

- Prefer `bmad_get_state`, `bmad_next_workflow`, `bmad_read_artifact`, `bmad_validate_artifact`, and `bmad_create_artifact_from_template` over freeform planning docs.
- Preserve existing sprint tracking unless the user explicitly wants it reset.
- Keep story ordering and status values explicit and auditable.

## Procedure

1. Inspect project-local truth with `bmad_get_state`.
2. Check whether `sprint_status` already exists.
3. If missing, create it from the contract-backed template.
4. If present, read and validate it before changing anything.
5. Ensure story ordering and statuses reflect the actual next implementation slice.
6. Report the resulting sprint-status path and the next expected workflow, usually `bmad-create-story`.

## Completion Output

Report:
- sprint-status path
- whether it was created or updated
- stories/statuses affected
- next expected workflow
