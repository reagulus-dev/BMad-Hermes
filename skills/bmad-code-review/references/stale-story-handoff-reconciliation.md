# Stale Story/Handoff Reconciliation Review Pattern

Use this when an acceptance criterion or review note says to reconcile stale workflow/story references (for example an undefined future story ID, stale handoff target, or superseded bridge-story name).

## Review stance

Do not treat artifact-only reconciliation as complete until the stale reference class has been searched across the repo. Stale workflow IDs often survive in source comments, IPC/test copy, continuation docs, or sprint/story metadata even when `_bmad/state.json` is clean.

## Checklist

- Search the BMad live-state and handoff surfaces:
  - `_bmad/state.json`
  - `_bmad/sprint-status.yaml`
  - current story artifact
  - `CONTINUE-HERE.md` or equivalent continuation docs
- Search source for the stale identifier and adjacent wording:
  - exact stale story ID, e.g. `HLX-4.6`
  - old workflow name or handoff phrase, if known
  - comments around deferred work that may imply a non-canonical next story
- Classify findings:
  - Historical story/review text can remain if it is clearly quoted as history or explains the correction.
  - Live workflow state, next-step instructions, source comments, and operator-facing text should not imply an undefined canonical story.
- Prefer neutral future wording when no canonical story exists:
  - `future explicitly selected resolver story`
  - `future secrets-resolver story`
  - `not currently a canonical STORY-ID`
- If the stale reference appears in source comments and the story AC includes stale handoff reconciliation, a small comment-only cleanup is in scope for the review/artifact reconciliation commit.

## Example

A bridge story required removing stale `HLX-4.6` handoff wording before selecting Epic 5. State and continuation docs were clean, but source comments in `notificationIpc.ts` still said `replace in HLX-4.6` / `HLX-4.6 will integrate a real secrets resolver`. The review normalized those comments to a future explicitly selected resolver story and recorded the cleanup in the passing review notes.
