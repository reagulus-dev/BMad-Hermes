---
name: bmad-help
description: Answer BMad workflow questions and recommend the most appropriate next BMad skill or tool-backed workflow.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, help, workflow-guidance]
    related_skills: [bmad-state-check, bmad-operating-model, bmad-workflow-plugin-implementation]
---

# BMad Help

## When to Use
Use when the user needs guidance on which BMad workflow, skill, or tool should be used next.

## Goal
Turn confusion into a clear next step grounded in the current BMad model.

## Procedure
1. Clarify the current project phase or problem.
2. Prefer project-local state and routing tools when available.
3. Recommend the most relevant workflow/skill and explain why.
4. Distinguish doctrine from mechanical tool actions.
5. Avoid vague answers when a concrete next workflow is available.

## Completion Output
Report the recommended workflow/skill, why it fits, and what information would change the recommendation.
