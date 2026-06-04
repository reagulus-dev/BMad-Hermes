# Tiny Blocker After Substantive Correction

Use this pattern when:

- A prior review BLOCKED a story on real product/source issues.
- A correction has clearly fixed those.
- The only remaining blocker is tiny and mechanical (e.g., unused import, trailing comma, whitespace, missing semicolon, tiny config drift).
- That tiny issue causes a real gate failure (e.g., lint under --max-warnings=0).

## How to handle (reviewer)

1) Initial review (tiny blocker):

- Still mark BLOCKED.
- Call out that substantive blockers are resolved.
- Required next action must be explicit and tiny:
  - “Run a tiny bmad-dev-story correction for STORY-ID: [1-line], then fresh bmad-code-review.”

2) Fresh review after tiny fix:

- Confine your re-review:
  - Confirm tiny blocker is resolved.
  - Confirm validation is clean.
  - Briefly confirm prior source blockers are still present and unchanged.
- If clean:
  - Issue PASS WITH NOTES immediately.
  - Route to bmad-state-check or next canonical gate.
- Do not:
  - Re-audit the whole story.
  - Re-open substantive blockers that were already resolved and not touched.
  - Invent new blockers in the same area just to “be safe.”

## Example: CardForge CF-E1-S6 (vi-import)

- First review: BLOCKED on COGS/profit semantics, missing breakdowns, wrong export route, missing tests.
- Correction: substantive fixes applied, tests added, lint claimed PASS.
- Second review: all source blockers resolved, but lint now FAILS due to unused vi import in analytics-and-exports.test.ts.
- Handling:
  - Blocked on tiny lint issue only.
  - Required next action: tiny correction (remove vi), then fresh bmad-code-review.
  - Fresh review:
    - Confirmed:
      - lint PASS,
      - tests PASS (23/23),
      - typecheck PASS,
      - prior source blockers still fixed.
    - Verdict: PASS WITH NOTES, next: bmad-state-check.

This is the canonical “tiny blocker after substantive correction” flow.
