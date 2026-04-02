---
name: bmad-document-project
description: Analyze an existing project and produce useful structured documentation or artifact inputs without freeforming vague implementation narratives.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, documentation, analysis, brownfield]
    related_skills: [bmad-generate-project-context, bmad-create-architecture, bmad-agent-tech-writer]
---

# BMad Document Project

## When to Use
Use for brownfield projects when the codebase needs clearer structure, architecture, or operational documentation.

## Goal
Produce documentation that improves understanding and can feed BMad artifacts.

## Procedure
1. Inspect project structure and runtime/build signals.
2. Identify the most valuable documentation gaps.
3. Prefer structured artifacts and auditable summaries over freeform essays.
4. Capture assumptions and unknowns explicitly.
5. Route outputs into the most relevant canonical artifact when appropriate.

## Completion Output
Report what was documented, what remains uncertain, and which canonical artifact or workflow should follow.
