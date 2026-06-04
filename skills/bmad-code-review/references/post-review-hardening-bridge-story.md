# Post-review hardening bridge story pattern

Use this when a BMad code review passes the story but leaves multiple concrete hardening items that should not disappear into loose notes.

## Trigger

After a `PASS` or `PASS WITH NOTES` review, create or recommend a dedicated bridge/tech-debt story when all are true:
- The reviewed story is valid enough to progress.
- The review found several bounded, actionable hardening items across the same feature area.
- The items are not required blockers for the reviewed story, but would be risky if left only in the review notes, continuation doc, or state summary.
- The next canonical feature story is uncertain, stale, or would be polluted by absorbing unrelated cleanup.

## Pattern

1. Keep the reviewed story's verdict truthful.
   - Do not downgrade a valid pass solely because follow-up hardening exists.
   - Do not mark release/QA readiness unless separately evidenced.
2. Name the bridge at the class/workstream level, not as an invented continuation of a stale feature ID.
   - Example: `HLX-TECHDEBT-2 — Epic 4 Monitor/Alert Hardening Sweep`.
   - Avoid inventing a canonical `HLX-4.6` if the project has not explicitly selected that story.
3. Convert every carry-forward note into an explicit acceptance criterion or dev note in the bridge story.
   - Race hardening.
   - Input/limit validation.
   - SQL/UUID validation.
   - Legacy settings sanitization.
   - Stale handoff/doc reconciliation.
4. Reconcile project truth together.
   - Reviewed story: append final review notes and point carry-forwards to the bridge.
   - `_bmad/state.json`: set current story/workflow to the bridge if it is the next actionable item.
   - `_bmad/sprint-status.yaml`: mark the reviewed story complete/reviewed and insert the bridge in the right order.
   - `CONTINUE-HERE.md`: replace stale next-story wording with the bridge and mark older handoff wording superseded.
5. Validate cheap artifacts before finalizing.
   - Parse JSON/YAML state files.
   - Run whitespace/diff sanity checks.
6. If code implementation was already committed, commit review/artifact/story updates separately.

## Pitfalls

- Do not leave non-blocking review findings only in a review section; they are easy to lose after compaction or handoff.
- Do not silently repurpose the next planned feature story for hardening unless the story artifact explicitly says so.
- Do not create a narrow one-off skill for a single story ID; keep this as a reusable BMad review-to-bridge pattern.
- Do not implement the bridge during review unless the user explicitly asks for dev-story execution.
