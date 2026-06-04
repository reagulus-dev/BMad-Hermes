# Interrupted or Compacted BMad Session Recovery

Use this reference when a prior BMad workflow was cut off, compacted without a useful summary, or the user says to resume/finish a correction from a previous session.

## Recovery pattern

1. Treat chat history and compaction summaries as advisory only; current files are the source of truth.
2. Inspect `_bmad/state.json`, `_bmad/sprint-status.yaml`, and the named story artifact before doing new work.
3. Resolve the user's named target first, especially if they mention a specific story such as `HLX-3.5`.
4. Reconcile status layers before advancing:
   - story metadata/status
   - live state fields
   - sprint-status entry
   - review/QA/evidence artifacts
   - relevant dirty worktree changes
5. If the previous workflow was a correction, verify that the correction's blockers are actually closed before selecting or creating the next story.
6. Only advance to the next workflow/story after the interrupted target is explicitly closed or the user asks to move on.

## Reporting standard

Keep the user-facing report short and operational:
- what target was recovered
- whether it is complete, blocked, or still inconsistent
- what files/state were reconciled
- the exact next recommended BMad workflow

Avoid narrating the whole historical session unless the user asks for a forensic log.
