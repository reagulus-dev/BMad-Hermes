---
name: bmad-sprint-status
description: Inspect and summarize sprint-status tracking to determine the current implementation position and likely next workflow.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, sprint-status, implementation, routing]
    related_skills: [bmad-sprint-planning, bmad-state-check, bmad-create-story]
---

# BMad Sprint Status

## When to Use
Use when sprint-status exists and you need a concise operational summary before the next implementation step.

## Goal
Turn sprint tracking into an explicit routing recommendation grounded in project-local state.

## Procedure
1. Read current project state and sprint-status.
2. Identify the active or next actionable story.
3. Surface blockers, ambiguous states, or missing story artifacts.
4. Recommend the next valid implementation workflow.
5. Prefer the tool/plugin layer over freeform interpretation.

## Completion Output
Report current story, status, blockers, and next workflow recommendation.
