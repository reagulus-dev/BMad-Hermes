---
name: bmad-dev-story
description: Execute a development story in a disciplined Alice/BMad manner using explicit state, validation, and evidence instead of vague completion claims.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, implementation, stories, validation, execution]
    related_skills: [bmad-state-check, bmad-code-review, bmad-evidence-reporting]
---

# Alice Dev Story

## When to Use

Use when implementing a concrete story, fix, or scoped code change for a project under `<project_root>`.

## Goal

Move a story from intent to validated implementation while preserving truthful status, project-local traceability, and clear evidence.

## Canonical Naming Rule

For Alice-managed live state, use `snake_case` consistently.

Preferred field names include:
- `active_workflow`
- `workflow_status`
- `current_story`
- `current_epic`
- `current_sprint`
- `last_artifacts`
- `last_evidence_path`
- `last_review_summary`
- `next_recommended_workflows`
- `updated_at`

Do not introduce new live-state updates using mixed camelCase names.

## Preconditions

Before starting, confirm:
- the project root is known
- `_bmad/state.json` has been checked or refreshed
- the target story or fix is explicit
- success criteria are clear enough to validate

If these are missing, stop and clarify or run `bmad-state-check` first.

## Execution Model

Alice is the orchestrator.
Use focused execution where appropriate, but keep the story and evidence trail honest.

Prefer this pattern:
1. define the target story or fix clearly
2. locate the canonical story or review anchor for this work
3. update `todo` with the workflow gates
4. inspect the codebase and relevant artifacts
5. execute directly for bounded work, or use `delegate_task` for focused implementation or research
6. run validation commands
7. collect concrete evidence using the `bmad-evidence-reporting` structure
8. append implementation notes to the relevant story or review thread when possible instead of creating a brand-new standalone file for every small change
9. update project-local `_bmad/state.json`
10. route to `bmad-code-review`

## Required Workflow Gates

Track these as todo items when applicable:
- scope confirmed
- implementation complete
- validation run
- review complete
- evidence recorded
- state updated

Only call the story operationally complete when all applicable gates are honestly satisfied.

## Validation Rules

Do not stop at code changes.

Run the strongest realistic validation available, such as:
- targeted tests
- build commands
- lint or typecheck where relevant
- runtime or user-flow checks when possible

Autonomous or YOLO-style implementation is acceptable during build-out, but completion claims must still wait for evidence.
If runtime verification is not available, say so explicitly.

## Evidence Requirements

Before claiming completion, gather:
- exact change target
- exact validation commands
- observed result
- runtime verification performed or not performed
- remaining unverified risk

Use the `bmad-evidence-reporting` minimum evidence block.

Store relevant evidence artifacts under `_bmad/artifacts/evidence/` when useful.
For fixes tied to an existing story, prefer appending dev notes and evidence references to that story thread rather than spawning a new orphaned note.

## Artifact Anchor Rule

For story-linked work:
- prefer the existing story artifact as the canonical anchor
- append dev notes, implementation notes, and evidence references there first
- create standalone evidence or review artifacts only when the scope is large, cross-cutting, or awkward to represent cleanly in the story thread

Do not create needless standalone markdown files for every small implementation update.

## Failure / Redirect Rules

Route to `bmad-correct-course` if available, or otherwise to an explicit correction workflow anchored to the story or review artifact, when:
- validation fails
- the issue is not reproduced or not understood
- review finds blocking problems
- state and reality materially disagree
- scope changes enough that the original story is no longer an honest implementation target

Do not hide failure behind optimistic wording.

## State Update Rules

After meaningful implementation work:
- update `active_workflow` if the current workflow changed
- update `workflow_status` to reflect reality
- update `current_story` if needed
- update `last_artifacts` with the most relevant touched story, review, or evidence paths
- update `last_evidence_path` if evidence was produced
- update `next_recommended_workflows` when the next step is clear
- refresh `updated_at`

Do not leave state stale after meaningful implementation work.

## Reporting Rules

Do not say:
- `done` without evidence
- `ready for QA` without recorded validation
- `ready for founder review` based only on implementation or tests
- `works` when runtime verification has not happened

Prefer honest labels such as:
- implemented, not yet reviewed
- reviewed, not yet runtime-verified
- build-passing, runtime-unverified
- blocked
- complete with evidence

## Pitfalls

- Do not equate coding with completion.
- Do not say `done` without evidence.
- Do not leave state files stale after meaningful work.
- Do not skip review when risk is non-trivial.
- Do not create artifact sprawl when a story anchor already exists.

## Completion Standard

A story is only operationally complete when implementation, validation, review, evidence, and honest reporting all line up.
