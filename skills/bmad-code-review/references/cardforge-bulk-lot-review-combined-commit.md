# CardForge CF-E5-S2 review pattern: uncommitted implementation + review reconciliation

Use this as a concrete example when a BMad code review starts from an uncommitted `bmad-dev-story` implementation rather than a prior implementation commit.

## Situation

- Story artifact had been created in one commit.
- The implementation, focused tests, evidence file, and BMad state/continuation updates were still uncommitted when review began.
- The review reran focused + full validation and found no blockers.
- Because source/test files were part of the reviewed work, a docs-only review commit would have been misleading.

## Correct handling

1. Review repo truth normally: story, state, sprint status, continuation doc, source diff, tests, evidence.
2. Rerun story-appropriate validation when practical.
3. Append the review verdict to the story artifact under `## Review Findings`.
4. Reconcile `_bmad/state.json`, `_bmad/sprint-status.yaml`, and `CONTINUE-HERE.md` to the fresh verdict.
5. If validation output includes non-blocking pre-existing/tooling warnings during an otherwise passing build, record them as notes rather than silently flattening the build to “clean”; do not turn them into blockers unless they are new/story-caused or gate-failing.
6. Commit with an implementation-accurate message that covers both source/test implementation and review artifacts, for example:

```text
feat(CF-E5-S2): bulk lot assignment and review
```

Use a docs-only commit only when the working tree truly contains only review/artifact changes.

## Verification bundle used

```text
corepack pnpm exec vitest run tests/unit/cf-e5-s2-bulk-lot-assignment.test.ts tests/unit/cf-e5-s2-bulk-lot-assignment-actions.test.ts
corepack pnpm run typecheck
corepack pnpm run lint
corepack pnpm test
corepack pnpm run build
DATABASE_URL=[REDACTED] corepack pnpm exec prisma validate
git diff --check
python3 - <<'PY'
import json, yaml
json.load(open('_bmad/state.json'))
yaml.safe_load(open('_bmad/sprint-status.yaml'))
print('artifact parse OK')
PY
```

## Durable lesson

When source/test implementation and review reconciliation are committed together, the commit should make that obvious. The BMad state should advance to the review verdict (`review_passed_with_notes` here) and the next workflow (`bmad-state-check` here), while QA/founder readiness remains explicitly unclaimed unless separately verified.
