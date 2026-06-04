# Review-to-Next-Story Handoff Pattern

Use when a BMad code review ends `PASS WITH NOTES` and the next workflow is story creation or development of the next planned story.

## Problem

A passing review often has non-blocking carry-forward notes. If those notes only live in the reviewed story, they can be lost when state advances to the next story.

## Pattern

1. Append the review findings to the reviewed story artifact first.
2. Classify each note:
   - blocker for current story: keep current story blocked and route back to dev
   - non-blocking carry-forward: keep reviewed story passable, but name the future story/boundary where it must be addressed
   - out-of-scope runtime discovery: preserve as future runtime/live-evidence work, not as an implementation claim
3. Reconcile `_bmad/state.json`, `_bmad/sprint-status.yaml`, and `CONTINUE-HERE.md` with the same wording.
4. If the next canonical story already exists in planning and naturally owns the notes, do **not** create a dedicated cleanup/bridge story. Record a carry-forward disposition in the reviewed story, `_bmad/state.json`, `_bmad/sprint-status.yaml`, and continuation docs that names the next story and the exact requirements it must absorb.
5. If immediately creating the next story, include the carry-forward as explicit acceptance criteria/dev notes in that new story when it belongs to that next story's boundary.
6. Create/recommend a dedicated cleanup or bridge story only when the notes are concrete, bounded, and **not** naturally owned by the next planned story, or when the next story is uncertain/stale.
7. Do not silently implement carry-forward work during story creation. Story creation may only encode the requirement unless the user explicitly asks for implementation.
8. Parse JSON/YAML after edits and run a cheap diff/whitespace sanity check.

## Examples

### Fold into the next canonical story

A Checkout Workers UI/control story passes with notes because cart/session state is still in-memory, controls are representational, and a renderer-only `window.__test...` helper exists for focused invalid-state tests. Planning already contains the next canonical story for worker-owned cart/session persistence. The handoff should:

- Keep the UI/control story as `PASS WITH NOTES`.
- State that no dedicated cleanup story is needed because the next canonical story owns the boundary.
- Record in the reviewed story, sprint status, state, and continuation docs that the next story must absorb the notes.
- Name concrete carry-forward requirements: replace in-memory placeholders where in scope, preserve one worker/profile/cart-session invariant in persisted state, source UI cart-state display from the new model, and remove/gate the test helper before persistent/runtime-backed behavior.
- Set the next workflow to state-check/story selection for the named next story, not back to the completed review.

### Preserve future runtime discovery without over-scoping the next story

A fixture-backed vendor parser review passes with notes because `session_invalid` markers are acceptable for offline fixtures but need tightening before live page-content use. The next story publishes typed monitor events. The handoff should:

- Keep the vendor parser story as `PASS WITH NOTES`.
- Add a carry-forward note to sprint/state/continuation docs.
- In the monitor-events story, require mapper/event-boundary guards so generic account/header/login copy cannot become a high-confidence `session_invalid` event.
- Preserve true live selector/page-content discovery for the later runtime/live-monitor story if that boundary is not part of the current story.
