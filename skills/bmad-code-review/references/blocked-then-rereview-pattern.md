# BLOCKED → Re-Review Pattern (class pattern)

Use when a BMad code review returns BLOCKED and the same story must be re-implemented and re-reviewed.

## Trigger

- A review verdict is BLOCKED with concrete findings.
- The story remains in-scope and must be corrected, not abandoned.

## Controller Responsibilities

1) Interpret BLOCKED:
   - Extract blocking issues as a short list.
   - Do not soften language; treat each as mandatory.

2) Direct dev-story agent:
   - Ask it to fix ONLY what is necessary to resolve blockers plus obvious related defects.
   - Require re-run of workspace validation:
     - typecheck
     - test
     - build
     - domain-specific checks (e.g., no-secret, runtime smoke)
   - Require it to append a “Dev Agent Record (post-BLOCKED fix)” section to the story artifact:
     - What was wrong (from the review)
     - What was changed
     - New validation evidence
   - Explicitly set next workflow: bmad-code-review (fresh review).

3) Fresh review:
   - Do not reuse the previous review’s trust.
   - Re-check:
     - All original blockers are resolved.
     - No new blockers were introduced.
   - Update story artifact and _bmad/state.json with the new review verdict.

## Pitfalls

- Do not:
  - Call the story “reviewed” just because it was reviewed before it was BLOCKED.
  - Trust that the dev-story agent fixed all blockers without re-checking.
  - Let the same story silently slide from BLOCKED → implemented → complete without a second explicit review.
