---
name: bmad-retrospective
description: Run an end-of-epic retrospective for completed implementation work and capture lessons learned without inventing unsupported progress claims.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, retrospective, implementation, review]
    related_skills: [bmad-state-check, bmad-sprint-planning, bmad-evidence-reporting]
---

# BMad Retrospective

## When to Use

Use when an epic's stories are done and the sprint tracker marks retrospective as optional/appropriate.

## Goal

Summarize what was completed, what was learned, and what should change next before returning to sprint planning.

## Rules

- Base conclusions on story/review/QA evidence, not vague memory.
- Prefer appending to existing project-local evidence threads over creating random standalone notes.
- If the epic is not actually complete, do not force a retrospective.

## Procedure

1. Verify the relevant epic/stories are actually done.
2. Review the most relevant story, review, QA, and evidence artifacts.
3. Summarize wins, misses, blockers, and process adjustments.
4. Record lessons in the project-local place the current workflow expects.
5. Route back to `bmad-sprint-planning` for the next cycle.

## Completion Output

Report:
- epic/story scope reviewed
- evidence sources used
- key lessons learned
- recommended next planning step
