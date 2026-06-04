---
name: bmad-state-check
description: Inspect project-local `_bmad/` truth before work and recommend the next valid BMad workflow.
version: 2.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, state, workflow, triage, project-status]
    related_skills: [bmad-project-init, bmad-dev-story, bmad-code-review]
---

# BMad State Check

## When to Use

Use before any major workflow, especially before planning, implementation, review, QA, founder-review, or release claims.

Also use when the user asks to verify a prior-session completion claim, reconcile whether a phase/story is truly complete, or identify outstanding implementation still implied by a plan.

## Goal

Ground BMad in project truth instead of assumptions.

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
5. preserved legacy material such as `_bmad-output/` when the project predates normalized BMad structure
6. `session_search` if the user references past work not visible in files and the relevant recall source is available

For interrupted or compacted-session recovery, also consult `references/interrupted-session-recovery.md`.

For gateway/session-store crashes involving `Errno 24` / “Too many open files” while writing `.sessions_*.tmp`, consult `references/session-store-fd-exhaustion-recovery.md` before trusting the interrupted chat state or advancing BMad gates.

For a concrete example of confirming a story is ready to move from `bmad-dev-story` to `bmad-code-review`, closing `PASS WITH NOTES`, and advancing the next story while keeping state/sprint/story/continuation docs aligned, consult `references/helix-epic4-status-gate-pattern.md`.

For resuming a previously held epic/story after a prerequisite epic reaches code-review completion, including the CardForge CF-E5 → CF-E4 handoff pattern and validator timing pitfall, consult `references/cardforge-cf-e5-to-cf-e4-resume-handoff.md`.

For founder/manual smoke feedback after a code-review pass — especially when the app is technically “complete” but runtime/browser QA was deferred — consult `references/founder-smoke-triage-pattern.md`.

## State Check Procedure

1. Confirm the project root.
2. Verify `_bmad/` existence directly. Do not rely only on file search results for directory existence; inspect the path directly or use a directory listing or similar direct check when needed.
3. Read `_bmad/state.json` if it exists.
4. Determine which state regime applies:
   - missing state
   - legacy-only state
   - partially normalized BMad state
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
8. For newly initialized projects or pre-scaffold requests, explicitly check planning completeness before endorsing implementation:
   - Search/read the project-local planning artifacts for PRD/product requirements, UX/UI design, architecture, and epics/stories.
   - Treat a brief `project_context.md`, lightweight `sprint-status.yaml`, or `CONTINUE-HERE.md` summary as useful seed context, not as substitutes for canonical PRD/UX/architecture artifacts.
   - If these artifacts are missing and the user follows the standard BMad workflow, recommend a compact planning pass before scaffolding or coding.
   - If the user explicitly chooses a fast spike/prototype path, record the waiver and keep implementation scope narrow.
9. If the user asks to move to a next story and names a target story ID, treat target resolution as the primary state-check task before recommending corrections to the previous story. Cross-check `_bmad/state.json`, sprint status, story artifacts, and planning docs for the named ID, then report whether it is ready, blocked, missing, or likely a typo.
9. If the user names a story ID that is not found exactly, do not invent the target or proceed from memory. Cross-check `_bmad/state.json`, sprint status, story artifacts, and planning docs for the nearest canonical anchor; report the mismatch briefly and proceed only with the artifact-backed target (for example, a typo like `HLX-2.34` may actually resolve to existing `HLX-2.4`).
10. Distinguish **PASS WITH NOTES** from **correction required**. Non-blocking carry-forward notes from a prior review should usually be preserved for future stories, not automatically converted into same-story correction work, unless the user asks for cleanup or the artifacts mark them as blockers.
11. If the user says a prior review was unauthorized or produced by an unauthorized model/provider, do not use that review as a valid progression gate during state-check. First look for a later fresh authorized review that explicitly supersedes it. If none exists, recommend/run `bmad-code-review` before next-story selection. If a fresh superseding review exists and passes, base next-story selection and carry-forward handling on that authorized review, while keeping the invalid review named only as superseded history.
12. When a story is `review_blocked` and `next_recommended_workflows` includes a correction:
   - Treat this as “fix this story” mode, not “start a new story” mode.
   - Recommend `bmad-dev-story` correction for the blocked story, following its “Review-Blocked Correction” pattern.
   - Do not select a new story until the blocked one has passed fresh review.
12. When the current story appears to be at a workflow boundary, cross-check all status layers before recommending or performing the next gate: `_bmad/state.json`, `_bmad/sprint-status.yaml`, the story artifact, `CONTINUE-HERE.md`, and git status/HEAD when the user asks where the repo was left.
- For a completion-audit request, explicitly reconcile:
   - claimed phase/story status from `_bmad/state.json` and artifacts
   - latest relevant git commit(s), HEAD, and dirty working-tree changes
   - implementation files and tests tied to the claimed scope
   - whether the exact previously recorded blockers are still present in source/config/build outputs, especially when the user asks whether a correction "finished"
   - validation/runtime evidence actually rerun or found in artifacts
   - remaining plan items that are outside the completed slice
   - stale state/docs that need reconciliation even when code is complete
   - status-layer consistency across live state, sprint status, and story metadata: if a story has moved beyond review into QA/runtime completion, prefer `status: completed` with separate `code_review_status` and `qa_status` fields rather than leaving the story's main status at `review_passed_with_notes`
- For runtime/browser smoke of locally running dev servers:
   - The browser tool often cannot reach 127.0.0.1/localhost even when curl can.
   - If browser_navigate fails with ERR_CONNECTION_REFUSED while curl succeeds:
     - Treat this as a known sandbox limitation; do NOT conclude the server is down.
     - Prefer:
       - Playwright E2E smoke via terminal (class-level skill: playwright-runtime-smoke), or
       - Exposing the dev server via a tunnel (e.g., ngrok) and using the browser tool on the public URL, or
       - Guiding the user through a short smoke checklist.
   - If the story is “Runtime Browser Smoke and Founder QA”, and the user asks you to run it:
     - If Playwright is available, run an automated smoke test covering core flows.
     - Report findings as evidence for that story instead of claiming it is “done” without runtime checks.
12. For founder/manual smoke feedback after a code-review pass:
   - Treat the user's observed runtime behavior as new evidence, not as a request to blindly implement fixes.
   - First map each issue against canonical PRD/epics/stories, current story acceptance criteria, and carry-forward notes.
   - Distinguish expected product semantics from defects. Example pattern: inventory/lot acquisition cost may be COGS and should not necessarily appear in Expenses, while a pence-facing business form may still be a real UX gap if the PRD says currency is GBP.
   - Distinguish source/static code-review completion from runtime/browser QA, founder approval, release readiness, and security/RLS hardening.
   - If a live app is reported as infinitely loading or unreachable, include a read-only runtime health probe when tools are available, but do not restart or mutate runtime state unless the user asks or the workflow scope clearly authorizes repair.
   - Recommend the next valid BMad gate in terms of evidence, e.g. `bmad-dev-story correction for <story> runtime/founder smoke`, rather than inventing an unrelated future epic.
12. When stale history is useful, preserve it as history but mark it as superseded by later evidence; do not leave older `runtime-unverified`, `pending`, or `not claimed` statements unqualified when a later QA gate closed that gap.
13. When the user explicitly asks “if no blockers, proceed with bmad-create-story,” continue directly into story creation after the state check instead of stopping at a recommendation. First record the state-check result, target-selection rationale, and evidence boundary, then invoke/follow `bmad-create-story` and keep `_bmad/state.json`, `_bmad/sprint-status.yaml`, the new story artifact, and continuation docs synchronized.
14. If a context compaction or restored todo list appears mid-work, reconcile it against actual filesystem/git/artifact state before acting. Mark already-completed checklist items complete in the session todo list and continue from the remaining validation/commit step; do not redo story selection or artifact creation just because an old todo says it is pending.
15. Produce a short operational summary.
16. Recommend the next valid workflow, or explicitly say the project is blocked.

## Legacy Handling Rules

- If `_bmad/state.json` is missing, recommend `bmad-project-init`.
- If only legacy BMad fields exist, report `legacy state detected; normalized BMad live-state missing or incomplete`.
- If normalized BMad fields exist but contradict repo or artifact reality, report `state present but reality requires refresh`.
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
- When a session was cut off or compacted, do not immediately advance to the next story just because state suggests the prior story is mostly done. First close or explicitly mark the named interrupted target, then recommend the next workflow.
- When story artifacts or files cannot be found via search, use direct paths from state.json (last_artifacts, current_story) and sprint-status.yaml (story_artifact) as authoritative. Do not loop identical search calls; fall back to read_file on known paths or terminal-based listing.
- Post-review handoff validator pitfall: the consistency probe can correctly fail when `state.json.current_story` still points at a now-`completed` story and `workflow_status` is `review_passed_with_notes` while the user asks to run state-check and proceed to the next story. Treat this as an expected handoff boundary, not a product blocker, after confirming the completed story has a valid PASS/PASS_WITH_NOTES review and no correction workflow. Select the next canonical story from sprint/planning truth, update `current_story` and `workflow_status` during create-story reconciliation, then rerun the probe and require it to pass after the new story is active.
- When a story is review_blocked, do not treat it as “done but with notes.” It is not allowed to advance until:
  - A correction is implemented,
  - A fresh bmad-code-review passes (even with notes),
  - And state/sprint/story artifacts are updated to implemented_not_reviewed → review_passed_with_notes.
- Multi-layer status drift is a common pitfall. When asked "where are we with <story>?":
  - Compare:
    - story artifact frontmatter status,
    - _bmad/state.json (current_story, workflow_status),
    - _bmad/sprint-status.yaml (story status),
    - CONTINUE-HERE.md / notes,
    - git status (uncommitted/untracked changes),
    - any "Dev Agent Record" at the bottom of the story artifact.
  - If they disagree, do not trust the most optimistic one. Call out the drift explicitly.
  - Treat the story as "not complete" until:
    - changes are committed,
    - all layers agree,
    - and any required gate (e.g., code review, QA) is recorded.

- When a review was completed in a prior turn of the same session and the verdict was recorded in that turn's output, but `state.json` still shows `workflow_status: implemented_not_reviewed` and `active_workflow: bmad-code-review`:
  - This is a stalled-state artifact reconciliation gap, not a request to re-run review.
  - The review already happened; the state just wasn't updated.
  - Correct sequence: update sprint-status.yaml (review_verdict, status: completed), update story artifact frontmatter and append Review Findings, update state.json (workflow_status → epic_completed or next story), update CONTINUE-HERE.md, then commit.
  - Do not re-run `bmad-code-review` just because state appears stale; confirm whether review output exists in the session before starting a new one.

- When epic completion is declared and CF-E3 doesn't exist yet (no story artifacts, user wants to use app with current features):
  - Mark epic `status: completed` in sprint-status.yaml.
  - Update state.json: `workflow_status: epic_completed`, `current_story: null`, `current_epic: null`.
  - Update CONTINUE-HERE.md with epic completion and "CF-E3 deferred" note.
  - Do not create placeholder CF-E3 story artifacts; defer until user activates the epic.
  - Commit all artifact updates together as one "complete epic" commit.

## Local web app runtime smoke (browser vs Playwright)

- Pitfall: the browser tool (browser_navigate) often cannot reach local dev servers on 127.0.0.1 due to sandboxing (ERR_CONNECTION_REFUSED), even when curl works.
- When runtime smoke or browser QA is required for a local Next.js/Node app:
  - Prefer:
    - Playwright E2E tests run via terminal (npx playwright test) as the primary “smoke” mechanism.
    - Or expose via a tunnel (e.g., ngrok) and use browser_navigate on the public URL.
  - Do not:
    - Assume browser_navigate to http://127.0.0.1:3000 will work.
    - Loop-retry the same failing browser_navigate call.
  - If the user asks “can you smoke this in the browser?”:
    - Explain briefly that the browser runtime is sandboxed.
    - Offer: (1) Playwright E2E smoke, (2) tunnel-based browser smoke, or (3) a guided checklist for the user.

## Completion Standard

A good state check gives BMad a reality-based starting point, an honest trust level, and a justified next move.

## Cross-Artifact Consistency Probe (re-runnable)

After any story selection, epic hold, or sprint edit, run the included
`scripts/validate_bmad_artifacts.py` from the project root. It deterministically
checks for drift across all four canonical files and prints the first divergence
it finds. Use it:

- immediately after editing `_bmad/state.json`, `_bmad/sprint-status.yaml`,
  `epics_and_stories.md`, or the current story artifact;
- before any commit that touches BMad artifacts;
- as the first step of the next `bmad-state-check` workflow, before reading
  the state files manually.

```bash
python3 ~/.hermes/skills/software-development/bmad-state-check/scripts/validate_bmad_artifacts.py [project_root]
```

The probe checks: state.json parses; sprint YAML parses; `current_epic`,
`current_story`, `current_sprint` agree across state.json and sprint YAML;
`current_story` exists in `sprint[].stories[]` and is not in a terminal or
deferred status while state.json claims it is the active story; the active
epic's status is `in_progress`; `active_story_artifact` exists on disk and its
frontmatter `story_id`/`epic` match state.json; `next_recommended_workflows`
names the current story when workflow_status is `story_created`/`in_progress`;
`CONTINUE-HERE.md` mentions the current story and epic; the planning doc has a
`### <current_story>` heading.
