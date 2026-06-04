# Deferred-Epic Activation + In-Flight Epic Hold (CF-E4 → CF-E5)

Worked example from CardForge on 2026-06-01. Use this pattern when the user explicitly
asks to pause the in-flight epic and pivot to a previously-deferred epic.

## Trigger

User said:

> "Put CF-E4 on hold. Tackle story 1 at a time. Go with Option C."

That single message is three distinct instructions stacked together. Treat them as a
single coordinated handoff, not three independent edits.

## What the four files must look like at the end

### `_bmad/artifacts/planning/epics_and_stories.md`

- Promote the target epic from a one-liner under `## Deferred Epics` to a real
  `## Epic CF-E5 — <name>` section with a `### <story-id>` sub-block per planned story.
- Each planned story's sub-block must say `Status: ready_for_dev` for the active one
  and `Status: blocked` (or `deferred`) for the siblings, with a `blocked_by:`
  pointer to the prior story.
- Keep a separate `## Deferred Epics` section but do not duplicate the activated epic
  there.

### `_bmad/artifacts/stories/<new-story>.md`

- Full story artifact (frontmatter + Story + Scope + Out of Scope + Implementation
  Expectations + Acceptance Criteria + Evidence requirements + Carry-forward
  sections for the blocked siblings).
- In scope, call out exactly the *narrow* work that fits one review cycle. The user
  asked for one-story-at-a-time: do not pre-scope the future stories here.

### `_bmad/sprint-status.yaml`

- Top-level `current_epic`, `current_story`, `current_sprint` all point at the new
  active story.
- The held epic block: `status: on_hold` with a one-line `hold_reason:` quoting the
  user. Its non-completed stories: `status: deferred` with a `deferral_reason:` that
  names the resume condition.
- The activated epic block: `status: in_progress`, the active story is
  `ready_for_dev`, and all sibling stories are `status: blocked` with explicit
  `blocked_by:` lines and a `deferral_reason:` describing what each sibling will do
  when unblocked.
- Append (do not rewrite) new `carry_forward_concerns:` entries that name:
  - the hold and its resume trigger,
  - the new active story's no-scope-absorption rule,
  - the blocked-sibling rule ("do not start sibling N+1 from sibling N").

### `_bmad/state.json`

- `current_epic`, `current_story`, `current_sprint`, `workflow_status`,
  `active_workflow`, `active_story_artifact` all point at the new active story.
- `last_artifacts` includes the new story artifact path plus the modified planning
  doc and sprint YAML.
- `last_review_summary` summarises the hold + the activation in one or two sentences.
- `next_recommended_workflows` is exactly `["bmad-dev-story for <new-story>"]`.
- `state_check.notes` gains explicit notes for: the hold, the activation, the
  blocked-siblings rule, and the trust level rationale.

### `CONTINUE-HERE.md`

- "Current Status" header: new active story, with a one-paragraph narrative naming
  the hold and the activation.
- "Completed Work" gains a one-line note about the hold (do not rewrite history).
- "Next workflow" line points at the new active story and explicitly forbids
  advancing the held epic or starting the blocked siblings.
- "Canonical Planning Artifacts" / "Active story" pointer updated to the new story.

## Why one coordinated edit, not a sequence

If you do these four files in sequence, a context-compact or crash mid-sequence
leaves state pointing at one epic and the planning doc pointing at another. The
next session's `bmad-state-check` will then either (a) silently trust the most
optimistic layer, or (b) refuse to advance because of the drift. Doing it as a
single intentional handoff also makes the eventual commit (when requested) a
clean single-commit story selection boundary, which is much easier to revert if
the user changes their mind.

## Pitfalls specific to this transition

- Do not mark the in-flight epic `status: completed`. It is not done; the user
  paused it. `on_hold` is the correct label; `completed` would let a future
  session silently re-allocate its remaining work.
- Do not mark the held epic's already-reviewed stories as anything other than
  `completed`. Only the not-yet-started stories should be `deferred`. Otherwise
  you lose the audit trail of which stories already passed review.
- Do not delete the held epic's `next_recommended_workflow` strings on its
  already-reviewed stories. They preserve the audit trail and let a future
  re-activation re-derive state cleanly.
- Do not let the held epic's `hold_reason` grow into a paragraph. One line,
  naming the user instruction and the date, is enough. The longer narrative
  belongs in `CONTINUE-HERE.md` or the new active story's "Context" section.
- The activated epic's blocked siblings must use the `blocked_by:` field, not
  freeform text in `deferral_reason:`. Future automation will rely on the field.
- If the held epic's `status: on_hold` is a new label for this project, expect
  YAML lint or downstream tools to not recognize it. That is fine; document it in
  `bmad-operating-model` so the next session knows the label is intentional.

## Re-activation (resume) procedure

When the user later says "resume CF-E4":

1. Run `bmad-state-check`; do not blindly trust the held epic's
   `next_recommended_workflow` pointers, since they may be stale.
2. Mark the held epic `status: in_progress` again, with a one-line `resume_note:`
   (not `hold_reason`).
3. Mark its previously-`deferred` stories back to their pre-hold status
   (`ready_for_dev` for the next-to-implement one, etc.).
4. The activated-then-paused epic gets `status: paused` (not `on_hold`,
   not `completed`) and its stories get the appropriate `paused` sibling state.
5. Update `CONTINUE-HERE.md` and `_bmad/state.json` in the same coordinated edit.

This is symmetric to the activation procedure. A future session that finds
`status: paused` knows immediately that this epic was once activated, paused
mid-flight, and is waiting on a different epic to finish.
