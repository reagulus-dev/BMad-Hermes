---
name: bmad-create-story
description: Create or initialize the canonical story artifact for the next backlog item using BMad contracts and synchronized sprint status.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, story, implementation, artifacts]
    related_skills: [bmad-sprint-planning, bmad-dev-story, bmad-artifact-policy]
---

# BMad Create Story

## When to Use

Use when sprint tracking identifies a backlog story that should become the active implementation artifact.

## Goal

Create the story file in the canonical location and move the story into a valid implementation-ready state without freeforming the document.

## Rules

- Use contract-backed creation and validation.
- Do not hand-write ad-hoc story markdown if the template/tool path is available.
- Keep sprint-status and story status synchronized.
- Prefer the plugin/tool layer over narrative-only execution.

## Procedure

1. Pre-step: run `bmad-sprint-status` (or equivalent) to:
   - Confirm the previous story’s completion.
   - Select the next story (e.g., HLX-3.2).
   - Ensure current_story is set in both:
     - `_bmad/state.json`
     - `_bmad/sprint-status.yaml`
   - For the first implementation/scaffolding story in a newly initialized project, verify that canonical PRD, UX/UI design, architecture, and epics/stories artifacts exist or that the user explicitly waived them for a spike/prototype. Do not treat `project_context.md` plus a lightweight sprint YAML as enough planning for normal BMad implementation.
   - Do NOT skip this; the story must be formally selected before creating its artifact.

2. Determine the target story key from:
   - Updated sprint-status, or
   - Explicit user direction.

3. Use `epics_and_stories.md` as the canonical source:
   - Read the story’s existing entry (e.g., HLX-3.2).
   - Preserve its scope, acceptance criteria, dependencies, and traceability.
   - Expand it into a concrete, implementation-ready artifact; do not invent new scope.
   - Do NOT repurpose a future story (e.g., HLX-3.4) to absorb open gaps from a previous
     story (e.g., HLX-3.3) unless the user explicitly approves. Instead, create a small
     continuation story (e.g., HLX-3.3b) to handle the gaps.

4. Continuation and finish-gate stories:
   - Use a continuation story (e.g., HLX-3.3b) when:
     - A story is review_passed_with_notes but has concrete open gaps:
       - UI is in-memory while DB migration/repository exists.
       - Migration not runtime-verified.
       - Missing IPC wiring, tests, or evidence.
   - Use a bridge/finalization story when:
     - The planned feature stories for an MVP/epic are code-review complete, but the app is not yet human-usable because auth, live DB/RLS, runtime smoke, deployment, or founder QA remains unverified.
     - The user asks what remains to “finish the web app/app/product.”
     - There is a real external/human setup blocker such as missing Supabase pooler `DATABASE_URL`, Auth provider settings, redirect URLs, or deployment env vars.
   - Rules:
     - Name continuation stories as `<previous>-b` (e.g., HLX-3.3b) or similar.
     - Name finish-gate stories at the epic level (e.g., `<EPIC>-S<N> — Auth, Supabase Runtime, and MVP Finish Gate`).
     - Mark previous stories as completed at their actual gate and route the new story to the bounded gap.
     - Keep continuation/finalization scope tight: only what is required to close the gaps.
     - Do not broaden into deferred product epics or silently turn a code-review pass into QA/founder/release readiness.

5. Ground the artifact in real project state:
   - Inspect existing code/UI (e.g., Electron renderer, vendor registry, navigation) to:
     - Confirm what is already implemented vs placeholder.
     - Align acceptance criteria with existing boundaries (IPC, renderer, packages).
   - When a new external-channel or storefront feature is being planned, also ground the architecture in any user-provided reference site or competitor example before story creation. If the reference clarifies the model (for example, Shopify-hosted storefront vs custom/headless storefront), update the technical plan first, then create the story from the clarified plan.
   - Call out “Out of Scope” explicitly where later stories are responsible.

5. If the story artifact already exists:
   - Treat it as the single source of truth.
   - Update scope/acceptance criteria only if they conflict with the epics_and_stories entry or current code reality.
   - Do not create duplicate artifacts.

6. If missing, create it:
   - Prefer the `story` template via `bmad_create_artifact_from_template`.
   - If the template/plugin tool is unavailable, create the smallest contract-shaped story artifact manually:
     - Metadata (artifact_type, project, epic, dependencies, traceability)
     - Story
     - Scope (concrete, no fluff)
     - Implementation expectations (where/how to change code)
     - Acceptance criteria (checklist style)
     - Out of Scope
     - Evidence requirements
     - Next recommended workflows
   - Label it as initialized/in_progress.
   - **Write the artifact to disk immediately.** Do not begin implementation until the story file is physically saved in `_bmad/artifacts/stories/` and BMad state/sprint/continuation docs are synchronized. If the user explicitly asks for the story to be saved before implementation, treat that as a hard sequencing gate, not a suggestion.

7. Validate the resulting story artifact:
   - Ensure it:
     - Is consistent with epics_and_stories.md.
     - Is technically plausible given current architecture.
     - Clearly separates this story from future stories.

8. Synchronize status:
   - Mark the story as `ready_for_dev` or `in_progress` in:
     - `_bmad/sprint-status.yaml`
   - Update `_bmad/state.json`:
     - current_story
     - workflow_status (e.g., “story_created”)
     - active_workflow (usually `bmad-dev-story` after creation)
     - next_recommended_workflows (e.g., ["bmad-dev-story for HLX-3.2"])
   - If a previous story just crossed a review boundary, reconcile its story frontmatter/status too (for example, `implemented_not_reviewed` → `completed` after PASS WITH NOTES is already recorded elsewhere).

9. Reconcile status/rules/continuation docs before handing off:
   - Update root `CONTINUE-HERE.md` or equivalent continuation files so the top-level "Current Status" and "Suggested Next BMad Workflows" point at the newly created story.
   - When adding a new epic/story after prior deferred labels or ad-hoc plans, reconcile epic numbering before saving state. Do not reuse an epic ID that has since been consumed by another completed/planned epic; create the next clean epic ID and update `epics_and_stories.md`, `_bmad/sprint-status.yaml`, `_bmad/state.json`, and `CONTINUE-HERE.md` together.
   - Also scan the early "active story / next workflow" sections for stale first-story text; rewrite those as historical/superseded or update them to the current story.
   - Do not let a stale continuation doc keep recommending a previously completed code-review while state/sprint point to the new story.
   - When story selection crosses an epic boundary, verify sprint-level `rules:` and `carry_forward_concerns:` still match the newly selected epic. If a broad earlier-slice rule would now contradict the canonical next story (for example "do not implement vendor-specific add-to-cart" when Epic 6 explicitly selects an add-to-cart story), reconcile the wording narrowly instead of leaving stale guidance to confuse the dev agent.
   - If the target epic was previously marked `completed` (all prior stories finished at review gate) and a new story is being added within that same epic, reopen the epic status to `in_progress` in `sprint-status.yaml`. Do not leave the epic at `completed` while its new story is `in_progress`; this breaks sprint-level consistency.
   - If the prior story has passed the review gate and the new story is selected, ensure `_bmad/state.json.completed_stories` includes the prior story where that project uses the field; do not leave completion state split between sprint YAML and live state.

9a. Activating a deferred epic while putting the in-flight epic on hold:
   - Use the canonical status labels `on_hold` (epic-level pause) and `deferred` (story-level pause) — see `bmad-operating-model` for the labels.
   - In a single coordinated edit, across all four files: set the previous epic `status: on_hold` with a one-line `hold_reason`; mark any non-completed stories in it as `deferred` (not `ready_for_dev` and not `in_progress`); activate the target epic in the same `epics:` block; register all sibling stories of the new active story as `blocked` with an explicit `blocked_by:` so future sessions do not silently start them.
   - Append new `carry_forward_concerns:` entries that explicitly state the hold, the resume condition, and the no-scope-absorption rule for the new active story and its blocked siblings.
   - Do this as a single "switch active epic" handoff, not a sequence of independent edits. If the user later resumes the held epic, the `hold_reason` and `deferral_reason` strings are the resume trigger.
   - See `references/deferred-epic-activation-and-handoff-2026-06-01.md` for the worked CardForge CF-E4→CF-E5 example.

9b. One-story-at-a-time cadence (user-requested):
   - If the user asks for one-story-at-a-time cadence ("tackle the stories one at a time", "implement story 1, then we'll decide on story 2", "let me review the first one before you start the second"), honor it literally:
     - Create only the first story artifact.
     - Register all future stories in the planning doc and sprint YAML, but mark them `status: blocked` with `blocked_by: <previous>`.
     - In the active story's scope/AC, include an explicit "carry-forward for <next>" section listing the work that is intentionally deferred.
     - Do not pre-create artifacts for the blocked siblings. They come into existence only after the gate that unblocks them.
   - This is stronger than the default "do not absorb future scope" rule: it forbids even artifact creation for the deferred siblings until the user gives the go signal.

10. Validate artifact consistency before finishing:
   - Confirm the new story artifact exists.
   - Confirm `_bmad/state.json` current_story / active_workflow / workflow_status match the intended handoff.
   - Confirm `_bmad/sprint-status.yaml` contains the new story and points `current_story` at it.
   - Parse story frontmatter, `_bmad/state.json`, and `_bmad/sprint-status.yaml` after edits.
   - Run the BMad artifact consistency probe after the new story is active. If it failed before story creation only because the prior reviewed story was already `completed`, record that as the expected post-review handoff boundary and require the post-creation probe to pass.
   - Run whitespace/diff hygiene when committing is requested (for example `git diff --check`) and fix trailing whitespace/blank EOF issues before commit.

11. Keep artifact diffs focused:
   - Avoid rewriting all of `_bmad/sprint-status.yaml` with a generic YAML dumper when only a timestamp/current-story change and one story append are needed; this creates noisy churn and hides the semantic change.
   - If a broad YAML reformat happens accidentally, revert that artifact and reapply a targeted text/style-preserving edit before committing.

12. Consent-guard pitfall:
   - If a batch artifact update script is blocked by a consent guard before making changes, do not retry via a different tool or claim the story was created.
   - Ask the user for explicit permission to create/update the BMad artifacts and commit/push, then perform the same intended artifact update once confirmed.
   - See `references/cardforge-cf-e4-s2-oauth-story-selection.md` for a concrete CardForge example.

13. Hand off to `bmad-dev-story` when the story is ready for implementation.

## Completion Output

Report:
- story key
- story artifact path
- whether it was created or already existed
- resulting story status
- next expected workflow
- reconciled artifacts (state, sprint, previous story status, continuation doc)
- commit SHA if the user requested a commit

## References

- `references/post-review-next-story-with-missing-plan.md` — pattern for creating the next story after a prior review pass when the validator initially reports handoff drift because the previous current story is completed, and when the next story references a missing/empty technical plan that should be created before handoff.
- `references/sprint-status-led-story-selection.md` — canonical pattern for sprint-status-led story selection and artifact creation (e.g., HLX-3.2).
- `references/continuation-story-pattern-2026-05-16.md` — pattern for using a continuation story (e.g., HLX-3.3b) to close material gaps without repurposing the next planned story.
- `references/epic-transition-after-bridge-review-2026-05-20.md` — pattern for moving from a bridge/tech-debt review into the first story of a new epic while preserving evidence boundaries and keeping YAML diffs focused.
- `references/next-story-after-review-pass-pattern-2026-05-20.md` — pattern for running state-check after a passing review, selecting the next canonical story, creating the story artifact, syncing BMad state/sprint/continuation docs, and handling compacted-session todo restoration safely.
- `references/cardforge-cf-e1-s2-after-review-state-check.md` — concrete pattern for progressing from a scaffold story with `PASS WITH NOTES` into the next canonical story: preserve `NOT_QA_VERIFIED`, carry non-blocking notes forward, mark the prior story completed at the code-review gate, create the next story, reconcile state/sprint/continuation docs, parse artifacts, and commit.
- `references/carry-forward-notes-next-story-2026-05-21.md` — pattern for absorbing non-blocking PASS WITH NOTES carry-forward items into the next canonical story with state-check rationale, AC/task/dev-note coverage, focused state/sprint/continuation edits, and post-commit validation.
- `references/finalization-story-after-feature-scope.md` — pattern for creating a bounded auth/runtime/deployment finish-gate story after planned feature stories are code-review complete but the app is not yet human-usable.
- `references/cardforge-rls-story-selection-2026-05-28.md` — pattern for selecting CF-E2-S3 after CF-E2-S2: creating a security/RLS story artifact, syncing state.json/sprint-status.yaml/CONTINUE-HERE.md, and wiring next_recommended_workflows to bmad-dev-story.
- `references/shopify-hosted-storefront-story-selection-2026-05-31.md` — pattern for turning a newly clarified external-channel/storefront plan into the first safe BMad story: update the plan from reference-site evidence, reconcile epic numbering, create a foundation-only story, sync state/sprint/continuation docs, and validate artifacts before handoff.
- `references/cardforge-cf-e4-s2-oauth-story-selection.md` — pattern for progressing from a reviewed Shopify foundation story into an OAuth connection story while preserving live-claim boundaries, syncing BMad state, and handling consent-guard blocks during batch artifact updates.
- `references/cardforge-cf-e4-s3-publishing-story-selection.md` — pattern for progressing from a reviewed Shopify OAuth story into the draft product-publishing story while preserving mocked/no-live-claim boundaries, owner-scope requirements, GBP→millipence price semantics, and state/sprint/continuation synchronization.
- `references/cardforge-cf-e5-s3-post-review-story-selection.md` — concrete CardForge pattern for treating an initial consistency-probe failure as a post-review handoff boundary, selecting CF-E5-S3, updating stale blocked-by anchors, synchronizing state/sprint/planning/continuation docs, and validating before commit.
- `references/deferred-epic-activation-and-handoff-2026-06-01.md` — pattern for activating a previously-deferred epic while simultaneously putting the in-flight epic `on_hold`, registering the future stories as `blocked` siblings, and reconciling state/sprint/planning/continuation in a single coordinated edit (CardForge CF-E4→CF-E5 example).
