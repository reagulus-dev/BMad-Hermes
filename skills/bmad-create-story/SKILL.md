---
name: bmad-create-story
description: Create or initialize the canonical story artifact for the next backlog item using BMad contracts and synchronized sprint status.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, story, implementation, artifacts]
    related_skills: [bmad-sprint-planning, bmad-dev-story, bmad-artifact-policy]
---

# BMad Create Story

## When to Use

Use when sprint tracking identifies a backlog story that should become the active implementation artifact.

## Goal

Create the story file in the canonical location and move the story into a valid implementation-ready state without freeforming the document.

## Rules

- Use contract-backed creation and validation.
- Do not hand-write ad-hoc story markdown if the template/tool path is available.
- Keep sprint-status and story status synchronized.
- Prefer the plugin/tool layer over narrative-only execution.

## Procedure

1. Determine the target story key from sprint-status or explicit user direction.
2. Check whether the story artifact already exists.
3. If missing, create it from the `story` template using `bmad_create_artifact_from_template`.
4. Validate the resulting story artifact.
5. Synchronize status so the story is no longer plain backlog once initialization is complete.
6. Hand off to `bmad-dev-story` when the story is ready for implementation.

## Completion Output

Report:
- story key
- story artifact path
- whether it was created or already existed
- resulting story status
- next expected workflow
