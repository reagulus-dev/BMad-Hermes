---
name: bmad-operating-model
description: Canonical operating model for BMad on Hermes — defines the normalized state schema, artifact tree, workflow lifecycle, gate order, and the split between policy skills and mechanical tools.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [alice, bmad, operating-model, workflow, policy, architecture]
    related_skills: [bmad-state-check, bmad-dev-story, bmad-code-review, bmad-evidence-reporting, bmad-qa-gate, bmad-artifact-policy, bmad-correct-course, bmad-project-init, bmad-state-migration]
---

# BMad Operating Model

## Purpose

This skill is the canonical operating model for BMad on Hermes.

Use it to understand or enforce:
- the normalized `_bmad/state.json` schema
- the canonical artifact tree
- the order of work from state check through implementation, review, QA, and correction
- the difference between policy skills and mechanical tools
- the rules for making honest completion claims

## Core Philosophy

BMad is allowed to work autonomously.
BMad is not allowed to outrun evidence.

Implementation is not completion.
Passing tests is not QA signoff.
Code review is not runtime validation.
Artifact presence is not proof of correctness.

The system exists to make project truth explicit.

## Canonical Naming Rule

For BMad-managed live state, use `snake_case` consistently.

Preferred keys include:
- `schema_version`
- `persona`
- `method`
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
- `blockers`
- `last_artifacts`
- `last_review_summary`
- `last_evidence_path`
- `next_recommended_workflows`
- `state_check`
- `legacy_bmad`

Do not create new BMad live-state fields in camelCase.
Legacy BMad camelCase fields may be preserved for historical compatibility, but normalized BMad fields are the live operational interface.

## Canonical State Schema

Use this schema as the target live-state model:

```json
{
  "schema_version": "2.0",
  "persona": "BMad",
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

## Canonical Artifact Tree

Route new BMad-managed artifacts here:

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

If the project already contains legacy material such as:
- `_bmad-output/`
- old OpenClaw/BMad docs
- root-level review directories
- older `_bmad/state.json` formats

preserve them unless the user explicitly asks for cleanup.

Use `bmad-state-migration` to normalize inherited state.
Treat legacy materials as historical evidence, not the preferred destination for new BMad-managed work.

## Workflow Lifecycle

The default Alice lifecycle is:
1. `bmad-state-check`
2. define the target story or fix
3. create or update todo gates
4. execute implementation work
5. run validation
6. record evidence
7. `bmad-code-review`
8. `bmad-qa-gate`
9. update state and artifact anchors
10. if reality diverges, route through `bmad-correct-course`

## Required Workflow Gates

For story execution, track these when applicable:
- scope confirmed
- implementation complete
- validation run
- review complete
- evidence recorded
- state updated

Do not claim operational completion while applicable gates remain untrue.

## Gate Semantics

### Review gate
Governed by `bmad-code-review`.
Possible verdicts:
- PASS
- PASS WITH NOTES
- BLOCKED

A review pass means the code review gate is satisfied.
It does NOT by itself mean QA passed or founder-review readiness.

### QA gate
Governed by `bmad-qa-gate`.
Possible verdicts:
- test-generated only
- code-reviewed, runtime-unverified
- runtime-verified for scoped flow
- founder-review ready for scoped flow
- blocked

For usability-sensitive flows, the strongest allowed verdict without runtime evidence is:
- `code-reviewed, runtime-unverified`

## Evidence Standard

Use the minimum evidence block from `bmad-evidence-reporting`:
- Change target
- Validation command(s)
- Runtime verification
- Result
- Unverified

Evidence should narrow uncertainty, not hide it.

## Artifact Anchor Policy

Default to the existing story as the canonical anchor.

Use this anchor order:
1. existing story artifact
2. existing review artifact for that story
3. existing QA artifact for that story or release thread
4. standalone artifact only when the issue is cross-cutting, release-wide, architectural, migratory, or too large to fit cleanly in the story thread

Do not create a new standalone markdown file for every small update.

## State Interpretation Labels

When checking project truth, use labels such as:
- missing state
- legacy-only state
- partially normalized state
- normalized but stale
- normalized and trustworthy enough for normal operation

Trust levels:
- `high`
- `partial`
- `low`

Prefer explicit uncertainty over optimistic inference.

## Canonical Status Language

Preferred progress labels when evidence is partial:
- implemented, not yet reviewed
- reviewed, not yet runtime-verified
- build-passing, runtime-unverified
- blocked
- complete with evidence

Do not silently upgrade status beyond what evidence supports.

### Epic- and Story-Level Status Labels (canonical set)

Use these labels for the `status:` field on epic and story entries in
`_bmad/sprint-status.yaml`. Do not invent synonyms; downstream tools and other
agents rely on these strings.

**Epic status:**
- `in_progress` — at least one story in the epic is in a non-terminal state.
- `completed` — every story in the epic has reached the code-review gate
  (and only the code-review gate; QA/founder/release readiness is a separate
  concept recorded on each story).
- `on_hold` — user explicitly paused the epic mid-flight. The epic is not
  done; the user asked for a different epic to advance first. Sibling
  non-completed stories are `deferred`. A `hold_reason:` field is required.
- `paused` — the epic was once activated, paused mid-flight, and is waiting
  on a different epic to finish. Symmetric to `on_hold` but indicates prior
  activation history. A `resume_note:` (not `hold_reason`) is required.

**Story status:**
- `ready_for_dev` — story artifact exists, dependencies met, no implementation
  has started.
- `in_progress` — `bmad-dev-story` is actively working on it.
- `implemented_not_reviewed` — code is written, tests pass, no review yet.
- `completed` — passed code review (with or without notes). Do not conflate
  with QA or founder-review readiness; that is a separate field.
- `review_blocked` — `bmad-code-review` found a blocker; treat as "fix this
  story" mode, not "start a new story" mode.
- `deferred` — sibling of an active epic, paused because a different story
  must finish first. A `deferral_reason:` and a `blocked_by:` pointer are
  required.
- `blocked` — a dependency on a different story is not yet satisfied. Same
  fields as `deferred`; the distinction is semantic (a deferred story is
  part of the same epic, a blocked story may be waiting on a different epic).

## Correct-Course Rule

When implementation, validation, review, QA, or repo reality diverges from the current story or claimed status, route through `bmad-correct-course`.

Typical triggers:
- validation fails
- QA disproves readiness
- review finds a blocker
- state and repo materially disagree
- scope drift invalidates the current story boundary

## Policy Skills vs Mechanical Tools

### Skills
Skills define policy and judgment.
Examples:
- `bmad-state-check`
- `bmad-dev-story`
- `bmad-code-review`
- `bmad-evidence-reporting`
- `bmad-qa-gate`
- `bmad-artifact-policy`
- `bmad-correct-course`

Use skills for:
- interpreting evidence
- deciding whether a gate is truly satisfied
- choosing the right artifact anchor
- reporting uncertainty honestly

### Tools
Mechanical tools should eventually handle repetitive and schema-sensitive operations.
Examples of future Alice tool responsibilities:
- initialize `_bmad/`
- read and validate normalized state
- migrate legacy BMad state
- append to canonical artifact anchors
- record evidence blocks consistently
- compute next recommended workflows
- recommend the next valid skill or workflow
- enforce template-backed artifact creation and legal section mutation

Use tools for:
- deterministic state updates
- artifact routing helpers
- migration and schema validation
- repetitive file operations that should not rely on memory alone
- workflow routing that should not be left purely to skill discretion

## Workflow Guidance Rule

`related_skills` metadata is useful for discoverability, but it is not a sufficient workflow engine.

If BMad is expected to know what comes next in a BMad-style way, plugin or tool support should provide:
- next valid workflow calculation
- recommended next skill
- blocked or stale-state detection
- gate satisfaction checks
- legal transition enforcement

Do not rely on skill cross-links alone to recreate BMad workflow guidance.

## Narrow Routing Rule

Workflow routing must be narrow by default:
- route explicitly to the next workflow/skill
- load only step-relevant policy
- enforce outputs with tools/contracts rather than memory or freeform prose

Split responsibilities cleanly:
- routing decides the active step
- the relevant workflow skill provides policy/judgment
- mechanical tools and artifact contracts enforce state transitions and output shape

Avoid broad ambient workflow loading or asking the agent to reconstruct structure from doctrine prose alone.

## Template and Contract Enforcement Rule

Core artifacts are contracts, not suggestions.

For important BMad/Alice artifacts, prefer porting and enforcing upstream BMAD templates and workflow output structures rather than letting agents freeform them.

Especially important first-slice artifacts are:
- story files
- `sprint-status.yaml`

For those artifacts:
- create them from registered templates when possible
- mutate only allowed sections for the active workflow
- validate required sections and legal statuses after changes
- preserve structured outputs so project audits are consistent across phases

## Non-Negotiable Rules

- Do not call coding `done` without evidence.
- Do not call test generation QA signoff.
- Do not call code review runtime validation.
- Do not infer completion from artifact presence alone.
- Do not leave `_bmad/state.json` stale after meaningful work.
- Do not hide blockers inside soft language.
- Do not create artifact sprawl when a canonical story anchor already exists.
- Do not treat a review as complete until all related artifacts are updated (state.json, sprint-status.yaml, story artifact, and continuation doc). If you skip this, the next session will not know the review happened and will redo the same work.
- When review notes (e.g., N1–N3) are addressed, update ALL affected artifacts in a single pass: code, tests, state.json, sprint-status.yaml, story artifact, and CONTINUE-HERE.md. Future sessions must be able to read the resolved state without reconstructing it from history.

## Completion Standard

BMad is operating correctly when implementation, validation, review, QA language, state, and artifacts all tell the same truthful story.
