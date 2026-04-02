---
name: bmad-state-check
description: Inspect project-local `_bmad/` truth before work and recommend the next valid Alice/BMad workflow.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, state, workflow, triage, project-status]
    related_skills: [bmad-project-init, bmad-dev-story, bmad-code-review]
---

# Alice State Check

## When to Use

Use before any major workflow, especially before planning, implementation, review, QA, founder-review, or release claims.

## Goal

Ground Alice in project truth instead of assumptions.

## Canonical Naming Rule

When reading or reporting Alice live state, prefer normalized `snake_case` field names such as:
- `active_workflow`
- `workflow_status`
- `current_epic`
- `current_story`
- `current_sprint`
- `blockers`
- `last_artifacts`
- `last_review_summary`
- `last_evidence_path`
- `next_recommended_workflows`
- `state_check.trust_level`

If the project still uses legacy camelCase-only BMad fields, say so explicitly and treat the state as legacy or partially normalized rather than pretending the live state is fully trustworthy.

## Inputs to Inspect

Primary sources, in order:
1. `<project_root>/_bmad/state.json`
2. recent artifacts in `_bmad/artifacts/`
3. `_bmad/notes.md` if relevant
4. current repo, build, and test reality when needed
5. preserved legacy material such as `_bmad-output/` when the project predates normalized Alice structure
6. `session_search` if the user references past work not visible in files

## State Check Procedure

1. Confirm the project root.
2. Verify `_bmad/` existence directly. Do not rely only on file search results for directory existence; inspect the path directly or use a directory listing or similar direct check when needed.
3. Read `_bmad/state.json` if it exists.
4. Determine which state regime applies:
   - missing state
   - legacy-only state
   - partially normalized Alice state
   - normalized but stale state
   - normalized and reasonably trustworthy state
5. Extract, when present:
   - `active_workflow`
   - `workflow_status`
   - `current_epic`
   - `current_story`
   - `current_sprint`
   - `blockers`
   - `last_artifacts`
   - `last_review_summary`
   - `last_evidence_path`
   - `next_recommended_workflows`
   - `state_check.last_checked_at`
   - `state_check.trust_level`
   - `state_check.notes`
6. Inspect whether the state appears stale or inconsistent with repo reality.
7. If needed, inspect recent artifacts or run read-only checks to confirm current truth.
8. Produce a short operational summary.
9. Recommend the next valid workflow, or explicitly say the project is blocked.

## Legacy Handling Rules

- If `_bmad/state.json` is missing, recommend `bmad-project-init`.
- If only legacy BMad fields exist, report `legacy state detected; normalized Alice live-state missing or incomplete`.
- If normalized Alice fields exist but contradict repo or artifact reality, report `state present but reality requires refresh`.
- If recent artifacts contradict state, say so explicitly.
- If implementation exists without review or evidence, do not call it complete.
- If `workflow_status` is `blocked`, do not pretend progress is available.

## Output Format

Use a compact structure:
- Project
- Current workflow state
- Current target
- Known blockers
- Most relevant recent artifacts
- Next valid workflow
- Trust level
- State freshness warning

## Recommended Interpretation Labels

Use language like:
- `missing state`
- `legacy-only state`
- `partially normalized state`
- `normalized but stale`
- `normalized and trustworthy enough for normal operation`

For trust, use:
- `high`
- `partial`
- `low`

## Decision Rules

- Prefer the repo and artifacts over wishful state.
- Prefer explicit blockers over optimistic wording.
- Prefer saying `unknown` or `unverified` over inferring a clean status.
- Do not upgrade a workflow to complete just because files exist.
- Do not infer runtime success from static review alone.

## Pitfalls

- Do not infer completion from artifact presence alone.
- Do not infer runtime success from static review alone.
- Do not skip state inspection just because the user sounds certain.
- Do not silently normalize mixed camelCase and snake_case mentally; call out schema drift when it matters.

## Completion Standard

A good state check gives Alice a reality-based starting point, an honest trust level, and a justified next move.
