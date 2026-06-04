---
name: bmad-autopilot
description: Use when James asks Alice to run a BMad-managed project forward autonomously through the next valid workflow gate while preserving strict implementation/review separation, serial local-model constraints, and evidence-backed state/artifact updates.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [alice, bmad, autopilot, orchestration, devon, workflow, evidence]
    related_skills: [bmad-operating-model, bmad-state-check, bmad-create-story, bmad-dev-story, bmad-code-review, bmad-correct-course, bmad-evidence-reporting, bmad-qa-gate, bmad-artifact-policy]
---

# BMad Autopilot

## Overview

BMad autopilot is Alice's reusable orchestration loop for advancing a BMad project without repeatedly asking James what to do next.

It does not weaken BMad gates. It automates the routing between them.

Autopilot must keep these boundaries intact:
- state check before action
- story-centered artifact anchoring
- implementation and review separation
- evidence before completion claims
- correction loops for review blockers or validation failures
- honest runtime language when runtime/device/browser verification has not occurred

Autopilot is especially useful for Apps Foundry work where Alice is the orchestrator and a slower local development worker such as Devon performs bounded implementation tasks.

## When to Use

Use this skill when the user says things like:
- "run BMad autopilot"
- "continue the next BMad story"
- "take this through the next workflow gate"
- "proceed autonomously until blocked"
- "use Devon for implementation, then review it"
- "start Phase 2 / next story / next slice" for a BMad-managed project

Do not use this skill for:
- one-off code review only; use `bmad-code-review`
- one-off implementation only; use `bmad-dev-story`
- project initialization; use `bmad-project-init`
- ambiguous product decisions that materially change scope; ask or create a decision artifact first
- parallel multi-agent execution against a single-concurrency local model

## Required Inputs

Autopilot needs:
- project root or project directory name
- intended project if multiple repos are active
- current BMad state/artifacts in the repo

If the user gives only a directory name, resolve it under `/home/reagulus/projects/<name>` unless repo reality indicates otherwise.

## Operating Rules

1. Alice remains the orchestrator.
2. Devon/local-dev is a single-lane implementation worker: do not run more than one Devon request or local-model worker concurrently.
3. Do not use MiniMax M2.7 for this workflow.
4. Use GPT/Codex-class review for fresh BMad code-review gates when available.
5. Implementation agents must not perform or claim final BMad code review.
6. Review agents must inspect repo truth, not trust implementation summaries.
7. Runtime/browser/device claims require runtime/browser/device evidence.
8. Keep artifacts tight; append to canonical story/review/QA anchors rather than creating sprawl.
9. Normalize live BMad state keys/statuses to `snake_case`.
10. Stop only when the requested gate is complete, a blocker is explicit, or the user-defined autopilot horizon is reached.

## Autopilot Horizon

Default horizon when the user does not specify one:
- For "next story": create or select the next story, implement it, validate, run fresh code review, perform bounded corrections until review passes or a real blocker appears, then reconcile state/artifacts.
- For "next gate": advance exactly one BMad gate and stop with evidence.
- For "until blocked": continue legal BMad transitions serially until a blocker, runtime-only requirement, external credential issue, or product decision is reached.

Do not silently expand from "next story" into an entire epic.

## Step-by-Step Loop

### 1. Load only the needed BMad policy

Always start with:
- `bmad-operating-model`
- `bmad-state-check`

Then load the next step's skill only when needed:
- `bmad-create-story` for story creation
- `bmad-dev-story` for implementation/correction
- `bmad-code-review` for review
- `bmad-correct-course` for divergence/blockers
- `bmad-qa-gate` for QA/runtime readiness
- `bmad-evidence-reporting` for final evidence wording

Avoid ambient loading of every BMad skill.

### 2. Resolve project truth

Inspect:
- git status and branch
- `_bmad/state.json`
- `_bmad/sprint-status.yaml` or equivalent sprint tracker
- current story artifact
- latest review/evidence artifacts
- `CONTINUE-HERE.md` if present

Classify state as one of:
- normalized and trustworthy enough
- normalized but stale
- partially normalized
- legacy-only
- missing state

If project state and git reality materially disagree, use `bmad-correct-course` before implementation.

### 3. Determine next legal workflow

Prefer project-local plugin/tool guidance when available.

If no plugin guidance is available, infer conservatively from:
- current_story status
- sprint-status ordering
- latest review verdict
- unresolved blockers
- carry-forward notes

Do not skip directly from implementation to completion without review and evidence.

### 4. Create or select the story

If no current story exists but sprint-status identifies the next pending story:
- load `bmad-create-story`
- create or initialize the canonical story artifact from template/contract
- update sprint status/state consistently

If a current story exists:
- use it as the anchor
- do not create a duplicate story artifact

### 5. Implementation lane

For implementation or corrections:
- load `bmad-dev-story`
- prefer a bounded worker prompt for Devon when implementation is non-trivial
- include project root, story id, exact allowed scope, validation commands, artifact rules, and the instruction not to run final review
- because Devon is single-concurrency, wait for the run to complete before launching anything else against local-dev

Devon prompt skeleton:

```text
You are Devon, Alice's BMad development worker. Work in <project_root>.
Load bmad-dev-story. Target story: <story_id>.
Scope: <exact implementation/correction scope>.
Do not perform or claim bmad-code-review. Do not broaden scope.
Run these validations if applicable: <commands>.
Update only the allowed story/evidence sections with exact results.
Leave final status as implemented_not_reviewed or blocked with precise blocker evidence.
```

If Alice implements directly instead of using Devon, she must still preserve the same status boundary: implemented is not reviewed.

### 6. Validation lane

Run the project's documented validations.

Typical validation evidence:
- typecheck
- lint
- unit/focused tests
- integration tests where available
- build/package checks where relevant

If validation fails:
- do not run review as if complete
- route back through implementation/correction
- record the failure and fix attempt in the story artifact

### 7. Fresh review lane

After implementation validation passes or reaches the requested review point:
- load `bmad-code-review`
- run a fresh review from repo truth
- inspect diff, story artifact, validation evidence, and architectural contracts
- classify verdict as PASS, PASS WITH NOTES, or BLOCKED

Never accept Devon's implementation summary as the review.

If review is BLOCKED:
- convert each blocker into a bounded correction scope
- route back to implementation lane
- repeat validation and fresh review

If review is PASS WITH NOTES:
- record notes and carry-forward items explicitly
- do not convert notes into hidden blockers unless the review says they block the story

### 8. QA/runtime lane

Use `bmad-qa-gate` only when the story's scope requires QA/readiness language beyond code review.

Allowed status without runtime evidence:
- reviewed, not yet runtime-verified
- code-reviewed, runtime-unverified

Forbidden without runtime evidence:
- runtime verified
- founder-review ready
- live checkout/browser/device verified

### 9. Reconcile artifacts and state

Before final response, ensure:
- `_bmad/state.json` reflects the actual workflow status
- sprint-status/story status matches the review/QA gate reality
- story artifact contains concise evidence
- review artifact or review section exists for fresh review
- `CONTINUE-HERE.md` is updated if it is the project's continuation anchor
- git status is known and reported

Prefer patching the existing canonical story/review/evidence anchor over adding standalone files.

### 10. Final report format

Use a compact evidence-first report:

```text
BMad autopilot result: <status>
Project: <project>
Story: <story_id> — <title>
Gate reached: <gate>
Verdict: <pass/pass_with_notes/blocked/runtime_unverified>

Evidence:
- <command>: <result>
- <artifact path>: <what changed>
- Review: <fresh review artifact/path/verdict>

Unverified:
- <runtime/browser/device/live vendor claims not made>

Next recommended workflow:
- <specific skill/workflow and why>
```

## Dry-Run vs Real Autopilot

A dry-run is read-only and should stop after resolving the next legal workflow.

A real autopilot run must not stop just because the next legal workflow is a correction. If state is `review_blocked` and artifacts identify a bounded `bmad-dev-story correction`, proceed into that correction lane unless there is an unsafe working tree conflict, missing prerequisite, external blocker, or product/scope decision.

Use status labels carefully:
- `dry_run_next_action_identified`: read-only routing result.
- `blocked`: no safe legal action can proceed without external input.
- `implemented_not_reviewed`: correction/implementation completed and awaits fresh review.

Do not use vague labels such as `blocked-before-action` unless also explaining whether that means read-only dry-run only or a real stop condition.

## Stop Conditions

Stop and report precisely when:
- a product/scope decision is required
- credentials, device, browser, server, or external service is missing
- validation fails after a bounded correction loop and root cause is not obvious
- review remains blocked after reasonable serial correction attempts
- runtime verification is required but not available
- repo state is unsafe to modify, e.g. unrelated dirty changes that would be overwritten

## Common Pitfalls

1. **Letting the implementation worker self-review.** Devon can implement and validate; Alice or a separate review lane must perform fresh BMad code review.

2. **Parallelizing a single-lane local model.** The local-dev endpoint is slow and single-concurrency. Do not spawn parallel Devon runs or multiple simultaneous requests.

3. **Treating tests as QA signoff.** Passing tests may satisfy validation, but runtime/device/browser readiness needs matching runtime evidence.

4. **Creating artifact sprawl.** Append to the story/review thread unless the issue is cross-cutting or explicitly standalone.

5. **Skipping state reconciliation.** A passing review with stale `_bmad/state.json` is not an autopilot-complete state.

6. **Absorbing blockers into the current story silently.** If scope materially changes, route through `bmad-correct-course` or create a continuation story.

7. **Overloading the final report.** James prefers compact, evidence-heavy reports. Avoid duplicate prose and marketing language.

## Verification Checklist

- [ ] Loaded `bmad-operating-model` and `bmad-state-check` first
- [ ] Resolved project root and git status
- [ ] Identified current/next story from project-local truth
- [ ] Used the correct narrow BMad skill for the active step
- [ ] Kept Devon/local-dev serial if used
- [ ] Ran applicable validation commands
- [ ] Performed fresh BMad code review after implementation
- [ ] Routed review blockers back through bounded correction
- [ ] Used honest runtime/QA language
- [ ] Reconciled `_bmad` state, sprint status, story/review/evidence artifacts, and continuation docs where applicable
- [ ] Final response includes evidence, unverified items, and the next recommended workflow
