---
name: bmad-create-epics-and-stories
description: Decompose requirements and architecture into a canonical epics_and_stories artifact suitable for implementation planning.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, solutioning, epics, stories, decomposition, artifacts]
    related_skills: [bmad-create-architecture, bmad-check-implementation-readiness, bmad-dev-story]
---

# BMad Create Epics and Stories

## When to Use

Use after architecture is sufficiently stable and the work needs to be broken down into epics and implementable stories.

## Upstream Alignment

This skill ports upstream BMad epics-and-stories creation into Hermes.
Preserve the upstream intent:
- decomposition by user value
- strong linkage back to requirements and architecture
- actionable stories with acceptance criteria

## Artifact Contract

Primary output artifact:
- `epics_and_stories`

Preferred mechanics:
1. inspect contract with `bmad_get_artifact_contract`
2. create the artifact with `bmad_create_artifact_from_template`
3. update sections with `bmad_update_artifact_section`
4. validate with `bmad_validate_artifact`

## Recommended Inputs

- `prd`
- `architecture`
- `ux_design` when relevant

## Execution Pattern

1. Review the requirement and architecture anchors.
2. Create or load the canonical `epics_and_stories` artifact.
3. Decompose the solution into epics with coherent value boundaries.
4. Break each epic into stories that are:
   - implementable
   - testable
   - traceable back to requirements
   - specific enough for sprint planning
5. **For migration/refactoring epics**, ensure stories are ordered to minimize risk:
   - Story 1: Schema + DB migration (foundation)
   - Story 2: Core helpers/libraries (money, validation)
   - Story 3: Server actions + UI forms
   - Story 4: Analytics + exports
   - Story 5: Test migration + regression suite
   - Story 6: Staging verification + founder QA
6. Ensure acceptance criteria and dependencies are explicit enough for downstream work.
7. Validate the artifact.
8. Route forward to `bmad-check-implementation-readiness`.

## Artifact Layout Convention

For non-trivial epics (≥3 stories, multi-area changes, or a custom planning doc would meaningfully clarify scope), the canonical layout is **two artifacts, not one**:

- `_bmad/artifacts/planning/<EPIC-ID>-<short-name>.md` — the long-form planning doc: Motivation (with observed-failure table if applicable), Non-goals, Target architecture, Stories (with one-line summaries), Out-of-scope carry-forward, Evidence expectations per story, Effort estimate, Risk-ranked list with mitigations.
- `_bmad/artifacts/planning/epics_and_stories.md` — gets a new `## Epic <EPIC-ID>` block appended in the same format as the existing CF-E1..CF-E5 blocks. The block contains: status, source-artifact link, epic goal, brief story summaries, Out of scope, and an explicit Carry-forward from prior epics section.

For trivial epics (1-2 stories, contained to one area, well-understood scope), a single epic block in `epics_and_stories.md` is fine. Default to the two-artifact layout for any epic the operator pauses to think about.

## Story Skeleton Conventions

Each story artifact should be **lean** (typically 100-200 lines), template-driven, and match the existing `bmad-create-story` frontmatter. The recommended sections:

1. **Frontmatter**: `artifact_type`, `project`, `epic`, `story_id`, `title`, `status`, `created_at`, `updated_at`, `canonical_path`, `dependencies`, `traceability`, `code_review_status`, `qa_status`.
2. **Story** (the user-voice one-liner).
3. **State-check selection rationale** (when the story is opened via bmad-state-check; cite the prior workflow output).
4. **Pre-flight / Cutover steps / Scope** (whichever applies; use a numbered list with sub-bullets for exact commands).
5. **Acceptance criteria** as a checklist, not prose.
6. **Out of scope** as a bulleted list, called out explicitly to prevent scope creep.
7. **Rollback plan** for any story that touches a running system (cutover, data migration, auth replacement, deploy pipeline).
8. **Evidence expectations** with the exact artifact paths under `_bmad/artifacts/evidence/`.
9. **Carry-forward** naming the prior epics/stories that are partially or fully superseded.
10. **Next workflow** (which BMad workflow runs after this story closes).

## Guardrails

- Do not produce placeholder stories with vague “do X” language.
- Do not detach stories from architectural reality.
- Keep story boundaries honest and implementation-relevant.
- **Do not mutate `sprint-status.yaml` or `state.json` during planning.** Those edits belong to the `bmad-state-check` / `bmad-sprint-planning` / `bmad-create-story` workflows, not to freeform planning. A planning doc can recommend a state change; only the workflow tools perform it.
- **Preserve superseded work, do not delete it.** When a new epic supersedes a prior story (e.g. self-hosted migration supersedes a Vercel workaround), mark the prior story `status: superseded` with a `superseded_by` field. The audit trail is the institutional memory; `git log` and `sprint-status.yaml` are the durable record of why the codebase looks the way it does.
- **Risk-rank with mitigations, not just bullets.** For any non-trivial epic, the Risks section should be a ranked list where each risk is paired with a concrete mitigation. Unranked "things that might go wrong" lists are a smell.
- **Scary operations get pre-flight + rollback plans.** Any story that does a data migration, an auth replacement, a deploy cutover, or a destructive irreversible action (project cancellation, schema drop, force-push) must have a `Pre-flight` section (what to verify days/hours before) and a `Rollback plan` section (exactly what to do if it breaks). Do not ship a cutover story without both.

## Completion Standard

Complete when the `epics_and_stories` artifact (and the sibling planning doc, if the epic warrants one) is validated and ready for implementation-readiness review. The epic block in `epics_and_stories.md` is the lightweight index; the planning doc carries the long-form reasoning.
