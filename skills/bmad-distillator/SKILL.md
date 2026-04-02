---
name: bmad-distillator
description: Distill large messy source material into the smallest structured set of durable findings that downstream BMad workflows actually need.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, distillation, synthesis, context]
    related_skills: [bmad-index-docs, bmad-document-project, bmad-generate-project-context]
---

# BMad Distillator

## When to Use
Use when the available source material is too large or noisy to carry directly into the next workflow.

## Goal
Compress source material into a high-signal, workflow-ready synthesis.

## Procedure
1. Identify the downstream decision or artifact that needs input.
2. Extract only the facts, constraints, and open questions that matter.
3. Remove duplication and low-signal detail.
4. Preserve traceability to original sources when possible.
5. Hand the distilled output into the next canonical workflow.

## Completion Output
Report what was distilled, what was intentionally omitted, and what workflow should consume the result next.
