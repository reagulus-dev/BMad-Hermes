---
name: bmad-state-migration
description: Audit and non-destructively extend an existing project-local `_bmad/state.json` from legacy BMad usage so Alice/Hermes can use it as a stronger live state source without destroying workflow history.
version: 2.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, migration, state, alice, project-upgrade]
    related_skills: [bmad-state-check, bmad-project-init, bmad-evidence-reporting]
---

# Alice BMad State Migration

## When to Use

Use when a project already has `_bmad/` from prior BMad/OpenClaw/plugin usage, but the existing `state.json` is too weak to serve as a trustworthy live operational state for Alice.

Typical signals:
- `_bmad/state.json` exists and contains meaningful workflow history
- top-level fields are thin, often limited to phase/workflow/history
- workflow records have empty or inconsistent output paths
- docs, artifacts, and repo reality disagree
- the user explicitly wants Alice/Hermes to adopt the existing project without destroying prior BMad history

## Goal

Preserve the legacy BMad ledger while adding normalized Alice-managed live-state fields so current truth, blockers, evidence, and next workflow can be represented explicitly.

If the plugin/tool surface supports it, prefer a mechanical migration tool first, then use this skill to audit the result, interpret trust honestly, and decide the next workflow handoff.

## Core Principle

Do not replace the old BMad state model outright.
Extend it non-destructively.

Keep history.
Add live state.
Mark trust honestly.

## Canonical Naming Rule

For Alice-managed live state, use `snake_case` field names consistently.

Do not introduce or extend mixed casing such as:
- `projectName`
- `projectPath`
- `createdAt`
- `currentPhase`
- `activeWorkflow`
- `workflowStatus`
- `currentStory`
- `updatedAt`
- `stateCheck`

Preserve legacy field names only as inherited historical data.
Treat normalized Alice fields as the live operational interface.

## Inputs to Inspect

1. `{project-root}/_bmad/state.json`
2. `{project-root}/_bmad/config.yaml`
3. recent files under `{project-root}/_bmad/artifacts/`
4. recent files under legacy BMad output directories, often `_bmad-output/...`
5. repo truth such as `git status`, recent commits, changed files, and relevant source files
6. BMad workflow bundle under `{project-root}/_bmad/bmm/` if present

## Audit First

Before changing anything:
1. Read the current `state.json` completely enough to understand its schema.
2. Count legacy workflow history entries.
3. Count entries with empty or missing output paths.
4. Inspect the latest artifact mtimes.
5. Compare recent workflow history to recent git history.
6. Inspect at least one recent workflow chain end-to-end, for example `correct-course -> dev-story -> code-review`.
7. Decide whether the state is:
   - trustworthy as history
   - weak as live control
   - stale
   - contradictory

## Expected Legacy Pattern

A common legacy schema looks like:

```json
{
  "projectName": "...",
  "projectPath": "...",
  "createdAt": "...",
  "currentPhase": "implementation",
  "activeWorkflow": null,
  "completedWorkflows": []
}
```

Treat `completedWorkflows` as a ledger, not as sufficient live status.

## Migration Strategy

### Preserve the legacy ledger

Unless the user explicitly asks for a destructive redesign, preserve the original legacy fields and workflow history.

Typical legacy fields to preserve:
- `projectName`
- `projectPath`
- `createdAt`
- `currentPhase`
- `activeWorkflow`
- `completedWorkflows`

Preserve them either:
- unchanged in place, or
- copied into a dedicated `legacy_bmad` object if a clean normalization pass is desired

Do not destroy workflow history.

### Add normalized Alice-managed live-state fields

Add or normalize to this canonical structure:

```json
{
  "schema_version": "2.0",
  "persona": "Alice",
  "method": "bmad-hermes",
  "project_name": "<name>",
  "project_root": "<absolute-path>",
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
    "last_checked_at": "<UTC-ISO-8601-or-null>",
    "trust_level": "partial",
    "notes": []
  },

  "legacy_bmad": {
    "preserved": true,
    "completed_workflows": []
  }
}
```

## Trust Level Rules

Use `state_check.trust_level` to avoid false certainty.

Suggested values:
- `high` — history and live state align closely with repo and artifacts
- `partial` — history is useful, but there are gaps or contradictions
- `low` — major conflicts, stale state, or poor artifact traceability

Default to `partial` when inheriting a legacy state model unless reality proves otherwise.

## Backup Rule

Before writing any migration:
1. create a dated backup file beside the original state file
2. never mutate the only copy of the legacy state

Example:
- `_bmad/state.pre-alice-backup-YYYY-MM-DD.json`

Observed implementation pattern that worked well in the plugin:
- if `_bmad/state.json` exists, create a timestamped sibling backup before writing
- if `_bmad/state.json` does not exist but `_bmad/config.yaml` or `_bmad/core/config.yaml` does, allow migration to seed a new normalized state file without requiring a backup

## Seeding the Initial Alice State

Seed conservatively.

Good initial values:
- `workflow_status`: `idle` or `stale`
- `blockers`: explicit known blockers from the audit
- `last_artifacts`: a short list of the latest relevant real artifact paths
- `last_review_summary`: one-line reality-based summary
- `last_evidence_path`: latest strongest evidence artifact if one exists
- `next_recommended_workflows`: ordered next moves grounded in current truth
- `state_check.trust_level`: usually `partial` for inherited legacy state

Do not seed a completion-like status unless runtime truth actually supports it.

Observed defaults that worked well for real exported projects:
- infer `current_story` from the first actionable sprint-status story when legacy state does not provide one
- infer `current_phase` from resolved artifact locations, but prefer explicit legacy/current state values when present
- set `next_recommended_workflows` conservatively to `['bmad-state-check']` immediately after migration
- preserve explicit ambiguity as a blocker instead of auto-choosing among conflicting exported artifacts

## Canonical Artifact Policy Going Forward

For new Alice-managed work:
- every meaningful workflow should produce or reference an artifact
- avoid empty output paths when possible
- if a workflow record must lack an output, record that limitation explicitly in state or a note artifact
- prefer structured artifact folders under `_bmad/artifacts/`:
  - `stories/`
  - `reviews/`
  - `qa/`
  - `evidence/`
  - `corrections/`
  - `release/`
  - `handoffs/`
  - `state/`
  - `archive/`
- preserve legacy `_bmad-output/` history during migration
- normalize new Alice-managed artifacts without deleting old trails unless explicitly asked

## Canonical Docs Upgrade

Legacy BMad/OpenClaw projects often accumulate multiple conflicting go-live or status docs.
When migrating a real project, prefer one canonical current-truth doc and one canonical procedure doc.

Recommended model:
- `docs/release-status.md` -> current operational truth
- `docs/release-runbook.md` -> release or shipping procedure

Older overlapping go-live docs can be reduced to transition stubs pointing at the canonical docs.

## Sensitive Material Safety

During migration or cleanup, inspect whether the project contains local credential paths such as:
- `credentials.json`
- `credentials/`
- keystore files

If found, recommend explicit `.gitignore` protection before broader cleanup so migration work does not accidentally surface or stage sensitive materials.

## Verification After Migration

After writing the migrated state:
1. confirm JSON parses successfully
2. confirm the backup exists when a prior `_bmad/state.json` existed
3. confirm legacy workflow history count is unchanged
4. confirm legacy keys or equivalent preserved legacy data still exist
5. confirm normalized Alice fields exist
6. confirm latest artifact paths actually resolve
7. report the trust level honestly
8. if a mechanical tool was added, test both direct service/tool behavior and MCP-exposed behavior
9. for config-only real exports, verify migration succeeds with `backup_path = null`

## Output / Reporting

Report:
- backup path
- whether legacy history was preserved intact
- which normalized Alice keys were added
- current `state_check.trust_level`
- current blockers
- recommended next workflow
- whether the project is now:
  - legacy-only
  - partially normalized
  - normalized but stale
  - normalized and ready for normal Alice operations

## Pitfalls

- Do not overwrite legacy workflow history.
- Do not claim the legacy state is fully trustworthy if artifacts, docs, and repo reality disagree.
- Do not infer completion from artifact presence alone.
- Do not mark runtime-sensitive work complete without runtime evidence.
- Do not destroy `_bmad-output` just because Alice prefers cleaner routing.
- Do not continue schema drift by mixing camelCase and snake_case in the same live state.
- Do not treat config-only real exports as `missing` if supported `_bmad/config.yaml` or `_bmad/core/config.yaml` exists; they are migration candidates.
- Do not auto-resolve ambiguous exported artifacts like `prd.md` plus `prd-v2.md`; keep that ambiguity visible as a blocker/note.
- Do not assume post-migration state is fully normalized if legacy camelCase keys are intentionally preserved in place.

## Recommended Companion Skills

After migration, use:
- `bmad-state-check` to ground current truth
- `bmad-evidence-reporting` before completion claims
- `bmad-code-review` for progression gates
