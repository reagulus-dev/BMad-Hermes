---
name: bmad-index-docs
description: Build a compact index of available project documentation so later BMad workflows can navigate the docs without loading everything at once.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, docs, indexing, context]
    related_skills: [bmad-document-project, bmad-generate-project-context]
---

# BMad Index Docs

## When to Use
Use when a project has many docs and the next workflow needs a navigable map rather than full document ingestion.

## Goal
Produce a compact doc index with enough metadata to support later retrieval and reasoning.

## Procedure
1. Enumerate relevant docs.
2. Summarize each doc's purpose, scope, and likely usefulness.
3. Highlight stale, duplicate, or missing documentation.
4. Keep the output compact and navigable.
5. Feed the index into later workflows instead of repeatedly re-reading everything.

## Completion Output
Report indexed docs, key gaps, and the most relevant next docs/workflows to inspect.
