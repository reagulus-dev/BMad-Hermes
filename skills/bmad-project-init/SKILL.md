---
name: bmad-project-init
description: Initialize a project-local `_bmad/` workflow structure inside `<project_root>` for BMad + Hermes BMad operations.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, workflow, project-init, state, artifacts]
    related_skills: [bmad-state-check, bmad-dev-story, bmad-evidence-reporting]
---

# BMad Project Init

## When to Use

Use when a project under `<project_root>` needs the standard BMad local workflow structure.

Typical triggers:
- new project with no `_bmad/` directory
- existing repo needs to be brought under BMad conventions
- project has code but no explicit local workflow state
- inherited project needs a normalized BMad state and artifact layout

## Goal

Create a predictable project-local `_bmad/` layout so BMad can use skills, state files, and artifacts consistently without storing cognition in ad-hoc markdown.

## Canonical Naming Rule

For BMad-managed state, use `snake_case` consistently.

Preferred field names include:
- `schema_version`
- `project_name`
- `project_root`
- `created_at`
- `updated_at`
- `current_phase`
- `workflow_status`
- `active_workflow`
- `current_epic`
- `current_story`
- `current_sprint`
- `last_artifacts`
- `last_review_summary`
- `last_evidence_path`
- `next_recommended_workflows`
- `state_check`

Do not create new BMad state using mixed camelCase names.

## Standard Layout

Create this inside the project root:

```text
_bmad/
  state.json
  notes.md
  artifacts/
    stories/
    reviews/
    qa/
    evidence/
    corrections/
    release/
    handoffs/
    state/
    archive/
  templates/
```

## Legacy Compatibility Rule

If the project already contains legacy BMad or OpenClaw structures such as:
- `_bmad-output/`
- older root-level review folders
- legacy `_bmad/state.json`

preserve them unless the user explicitly asks for cleanup or migration.

Do not delete historical workflow evidence during initialization.
For inherited projects, prefer preserving legacy material and then routing future BMad-managed work into the canonical `_bmad/artifacts/` tree.

## Steps

1. Confirm the intended target project root and operate there; do not assume a specific parent directory.
2. Check whether `_bmad/` already exists.
3. If missing, create the standard directories.
4. Create `state.json` from the canonical BMad template.
5. Create `notes.md` with a short header explaining its purpose.
6. Do not overwrite meaningful existing state or artifacts unless the user explicitly asks.
7. If the project is new or being structured from scratch, strongly prefer one early setup or dependency story that clusters dependency selection, version pinning, environment prerequisites, and user-input-heavy setup decisions into a single place as much as practical.
8. Report the initialized paths and any pre-existing files that were preserved.

## Canonical `state.json` Template

Initialize with this model unless a migrated legacy state already exists:

```json
{
  "schema_version": "2.0",
  "persona": "BMad",
  "method": "bmad-hermes",
  "project_name": "<repo-slug-or-canonical-project-name>",
  "project_root": "<absolute-repo-path>",
  "created_at": "<UTC-ISO-8601>",
  "updated_at": "<UTC-ISO-8601>",

  "current_phase": "implementation",
  "workflow_status": "idle",
  "active_workflow": null,

  "current_epic": null,
  "current_story": null,
  "current_sprint": null,

  "blockers": [],
  "last_artifacts": [],
  "last_review_summary": null,
  "last_evidence_path": null,
  "next_recommended_workflows": [],

  "state_check": {
    "last_checked_at": null,
    "trust_level": "partial",
    "notes": []
  },

  "legacy_bmad": {
    "preserved": false,
    "completed_workflows": []
  }
}
```

## `state.json` Initialization Rules

Initialize with these principles:
- `schema_version` = `2.0`
- `project_name` = repo slug or canonical project name
- `project_root` = absolute repo path
- `method` = `bmad-hermes`
- `persona` = `BMad`
- `active_workflow` = `null`
- `workflow_status` = `idle`
- arrays default to `[]`
- nullable descriptive fields default to `null`
- `created_at` and `updated_at` should be current UTC time in ISO-8601 format
- `state_check.trust_level` should default to `partial`
- for a brand-new project with no inherited legacy data, `legacy_bmad.preserved` should usually be `false`
- for an inherited project that still carries old BMad history, do not synthesize fake history; migrate it separately using `bmad-state-migration`

## `notes.md` Rules

Use `notes.md` only for project-local notes that are:
- too local for Hermes memory
- too minor for a skill
- still worth keeping with the project

Do not turn `notes.md` into a giant journal.

## Verification

After initialization, verify:
- `_bmad/state.json` exists
- all canonical artifact directories exist
- paths point to the correct project root
- no unrelated project files were changed
- no meaningful existing state was overwritten blindly

## Pitfalls

- Do not assume the project must live under any specific filesystem parent; use the confirmed target project root.
- Do not store long-term procedural knowledge in project files; that belongs in skills.
- Do not overwrite existing `_bmad/state.json` blindly; inspect first.
- Do not scatter dependency and environment prerequisites across many tiny early stories if they predictably require user input; consolidate them into one setup-focused story where reasonable.
- Do not require symlinked workflow bundles or a literal OpenClaw plugin layout for BMad to function in Hermes.

## Completion Output

Summarize:
- project root
- whether `_bmad/` was newly created or already existed
- files created
- directories created
- any preserved existing state or artifacts
- whether legacy material such as `_bmad-output/` was detected and preserved
