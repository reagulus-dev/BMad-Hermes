# Partial Story Continuation / Rescue Pattern

Use when:
- A dev story was started in a previous session that was cut off.
- A context-compaction handoff says implementation/validation was mostly complete but finalization was pending.
- _bmad/state.json or CONTINUE-HERE.md indicates the story was “in progress,” “ready_for_dev,” `review_blocked`, or partially updated before the cut-off.

Treat all prior work as “partial + untrusted” until filesystem state, validation, and BMad artifacts are rechecked. A compaction summary is a useful map, not evidence by itself.

Steps:
1) Read:
   - _bmad/state.json: current_story, workflow_status, last_artifacts, next_recommended_workflows.
   - Story artifact: acceptance criteria, review findings, correction/evidence sections, and current status.
   - _bmad/sprint-status.yaml: current_story entry, status, review_verdict, and updated_at.
   - CONTINUE-HERE.md: last update for this story, if present.
   - Preserved todo state, if supplied by the session, to distinguish implementation work from finalization-only work.

2) Inspect filesystem:
   - New migrations, repos, services:
     - Confirm they exist, are exported, and match story scope.
   - Preload:
     - Confirm IPC bridge is exposed (e.g., window.helixRoutes).
   - Main process:
     - Confirm IPC handlers wired and using correct service.
   - Renderer:
     - Confirm the actual loaded renderer entry (e.g., nav-init.js) has been updated.
     - Confirm it uses the same API shapes as preload and main process.

3) Run validation:
   - If implementation may still be incomplete, run targeted validation first to localize failures, then full validation.
   - If the handoff says validation already passed but the session cut off before final reporting/artifact closure, rerun the validation suite before finalizing; do not rely only on pasted prior output.
   - Typical Helix/Electron stack: targeted Vitest for touched files, `pnpm -r run typecheck`, `pnpm -r run test`, `pnpm -r run build`, and `pnpm run db:migrate`.
   - If tests fail:
     - Assume prior session left inconsistent state.
     - Inspect failures; treat as concrete evidence of partial work.

4) Finalization-only continuation checklist:
   - Run `git status --short --branch` and `git diff --stat` to understand scope before reporting.
   - Remove accidental scratch/backup files from the worktree if they are clearly untracked implementation debris (for example `*.bak` created by the agent), but do not discard user-authored changes.
   - Parse/validate `_bmad/state.json` and `_bmad/sprint-status.yaml` after edits.
   - Re-read the story artifact to ensure status, parent acceptance checkboxes, correction section, validation evidence, and next workflow agree.
   - If acceptance criteria contain parent checklist items with checked children, update the parent item too; otherwise the story reads partially incomplete despite child evidence.
   - Preserve an honest status such as `implemented_not_reviewed` and route to fresh `bmad-code-review`; do not upgrade to QA/reviewed/completed without the matching gate.

5) Common partial patterns to expect:
   - Migration and repository exist, but:
     - Service not wired.
     - Main process IPC handlers missing.
   - Preload exposes window.X, but:
     - Renderer still uses placeholder or wrong method names/fields.
   - Renderer reads fields not present in DB rows (e.g., health vs status, description vs config).
   - Functions syntactically or logically broken (stray assignments, wrong control flow).

6) Fix:
   - Align:
     - Renderer ↔ Preload ↔ Main process ↔ Service ↔ DB repository.
   - Add or update focused tests where the mismatch was.
   - Update _bmad/state.json, sprint-status.yaml, and story artifact based on your validation, not the prior session’s claims.

7) Route:
   - Set next_recommended_workflows to:
     - fresh bmad-code-review for this story.
   - Record in CONTINUE-HERE.md when it is part of the project convention:
     - That continuation/rescue was performed.
     - What was partial, what was corrected, and current verified status.

Concrete HLX-3.5 finalization example:
- Prior session had already implemented route/proxy correction and run validation, but the context cut off after artifact update.
- Continuation action was not more feature work; it was final verification:
  - Re-run targeted route tests and full typecheck/test/build/db:migrate.
  - Remove stray `nav-init.js.bak` scratch file.
  - Parse `_bmad/state.json` and `_bmad/sprint-status.yaml`.
  - Reconcile story acceptance parent checkboxes and correction evidence timestamp.
  - Keep status `implemented_not_reviewed` and next workflow `fresh bmad-code-review for HLX-3.5`.
