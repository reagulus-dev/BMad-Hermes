# Helix BMad Dev Workflow Checklist (2026-05-21)

Use this as a quick reference when running bmad-dev-story on the Helix project.

## Pre-Implementation

- [ ] Confirm:
  - _bmad/state.json current_story and workflow_status.
  - _bmad/sprint-status.yaml story status.
  - CONTINUE-HERE.md top-level status.
- [ ] Read the story artifact:
  - Acceptance criteria.
  - Carry-forward notes (from prior reviews).
  - Non-goals and boundaries.

## Implementation

- [ ] Implement changes:
  - DB migrations (if applicable).
  - Repository/service helpers.
  - Orchestrator/runtime logic (if in scope).
  - Electron/renderer UI (if in scope).
- [ ] Keep sensitive data:
  - As opaque/redacted references only.
  - No raw credentials/cookies/tokens/OTP/payment details.
- [ ] Enforce:
  - One worker ↔ one profile ↔ one cart/session.
  - Unique constraints and ownership guards where relevant.

## Validation

- [ ] Run:
  - Targeted tests (DB, orchestrator, renderer).
  - Typecheck: per-package npx tsc --noEmit.
  - Build: per-package npx tsc --build.
  - db:migrate: node dist/cli.js migrate (if migrations changed).
- [ ] Use per-package commands:
  - Prefer npx vitest run, npx tsc --noEmit, etc.
  - Root scripts with pnpm -r or --filter may fail due to Corepack/shim issues.

## Artifact Updates

- [ ] _bmad/state.json:
  - workflow_status (e.g., story_implemented_review_pending).
  - next_recommended_workflows (e.g., bmad-code-review for <story>).
  - last_review_summary, last_evidence_path, updated_at.
- [ ] _bmad/sprint-status.yaml:
  - story status (e.g., implemented_and_review_pending).
  - next_recommended_workflow.
- [ ] CONTINUE-HERE.md:
  - Current status paragraph.
  - Active story status and next BMad workflow.

## Completion

- [ ] Commit implementation.
- [ ] Commit artifact updates.
- [ ] Route to bmad-code-review.
