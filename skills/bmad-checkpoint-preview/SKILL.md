---
name: bmad-checkpoint-preview
description: Prepare a structured checkpoint preview of current implementation progress for human review before deeper approval or continuation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, checkpoint, preview, review]
    related_skills: [bmad-dev-story, bmad-code-review, bmad-evidence-reporting]
---

# BMad Checkpoint Preview

## When to Use
Use when a human needs a concise walkthrough of current implementation state before deciding what happens next.

## Goal
Summarize purpose, changes, evidence, and risks in a reviewable format.

## Procedure
1. Identify the story or change scope.
2. Gather the most relevant artifacts, diffs, and evidence.
3. Summarize intended outcome, current reality, and open risks.
4. Avoid overstating confidence.
5. Recommend whether to continue, review, test further, or correct course.

## Completion Output
Report checkpoint scope, evidence examined, current risk level, and recommended next action.
