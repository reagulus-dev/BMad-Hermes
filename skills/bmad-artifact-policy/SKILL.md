---
name: bmad-artifact-policy
description: Story-centered artifact policy for BMad. Prefer appending to the relevant story/review/QA thread instead of creating new standalone markdown files for every small change.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, artifacts, documentation, stories, qa]
    related_skills: [bmad-dev-story, bmad-code-review, bmad-qa-gate, bmad-evidence-reporting]
---

# BMad Artifact Policy

## Goal

Keep BMad traceable without producing artifact sprawl.

## Core Rule

Default to the existing story as the canonical anchor.

If a bug, fix, review, evidence note, or QA finding maps to an existing story, update or append to that story thread first before creating a new standalone document.

## Artifact Anchor Order

Choose the artifact anchor in this order:
1. existing story artifact
2. existing review artifact for that story
3. existing QA or manual-test artifact for that story or release thread
4. standalone artifact only if the work is cross-cutting, release-wide, architectural, migratory, or too large to fit cleanly in the story thread

Story anchor wins unless the work is clearly cross-story, release-wide, or architectural.

## Append vs Create

Story-scoped review and QA findings always go into the story artifact:
- `## Review Findings` — code review verdict and findings
- `## QA Findings` — QA results and test outcomes
- `## Evidence / Verification` — runtime checks, test commands, evidence links

### Create a standalone artifact only when:
- the work is cross-story or cross-epic
- the issue affects release readiness broadly
- the issue is architectural or process-wide
- a major QA sweep spans many stories
- a migration, release audit, or runbook is needed
- a correction log spans multiple stories or workflows

## Canonical Artifact Tree

Prefer these canonical folders under `_bmad/artifacts/`:
- `stories/`
- `reviews/`
- `qa/`
- `evidence/`
- `corrections/`
- `release/`
- `handoffs/`
- `state/`
- `archive/`

Preserve legacy `_bmad-output/` or older project note structures when they already exist, but route new BMad-managed work toward the canonical tree unless the user explicitly asks otherwise.

## Canonical Story Sections

When using a story as the anchor, prefer these sections:
- Story
- Acceptance Criteria
- Tasks / Subtasks
- Dev Notes
- Dev Agent Record
- Completion Notes
- File List
- Review Findings
- QA Findings
- Evidence / Verification

If the story file does not yet have Review Findings, QA Findings, or Evidence sections, append them cleanly instead of creating a throwaway side document.

## Small-Change Rule

Do not create a brand-new standalone markdown file for every small fix.
A small fix should usually update:
- the story thread
- the relevant review, QA, or evidence section
- `_bmad/state.json`

## Naming Guidance for New Standalone Artifacts

If a new artifact is genuinely warranted, use clear scoped folders and names:
- `_bmad/artifacts/corrections/YYYY-MM-DD-topic.md`
- `_bmad/artifacts/reviews/YYYY-MM-DD-story-or-topic.md`
- `_bmad/artifacts/qa/YYYY-MM-DD-topic.md`
- `_bmad/artifacts/release/YYYY-MM-DD-topic.md`
- `_bmad/artifacts/evidence/YYYY-MM-DD-topic.md`
- `_bmad/artifacts/state/YYYY-MM-DD-topic.md`
- `_bmad/artifacts/handoffs/YYYY-MM-DD-topic.md`

## Legacy Migration Guidance

For legacy projects, if you find root-level folders like `code-reviews/` or other stray review or note directories outside `_bmad/`, move or consolidate them under the appropriate `_bmad/artifacts/...` folder when the user wants cleanup.

If cleanup is not yet requested, at minimum treat those folders as legacy stores and avoid creating new parallel competing stores beside them.

When archiving legacy materials that are no longer canonical, prefer:
- `_bmad/artifacts/archive/`

## Anti-Patterns

Avoid:
- duplicate summary docs that restate current state
- separate mini-docs for every tiny fix when the story already exists
- orphaned dev-story, review, QA, or evidence notes with no traceable story anchor
- conflicting go-live or release-status docs
- mixing old and new artifact routing rules without saying which store is canonical

## Completion Standard

A good artifact strategy makes it easy to answer:
- what story this work belongs to
- what changed
- what was reviewed
- what was tested
- what remains unverified
- which artifact is canonical
