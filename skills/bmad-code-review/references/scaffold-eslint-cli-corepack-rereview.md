# Scaffold Re-review: Corepack + ESLint CLI Corrections

Use this when a scaffold/foundation story was previously BLOCKED on pnpm/Corepack metadata or deprecated `next lint`, then receives a focused correction.

## Fresh review checks

Run the declared package-manager path, not local binary fallbacks:

```bash
corepack pnpm --version
corepack pnpm install --frozen-lockfile
corepack pnpm lint
corepack pnpm typecheck
corepack pnpm test
DATABASE_URL='postgresql://user:***@localhost:5432/app' corepack pnpm exec prisma validate
corepack pnpm build
```

Also parse BMad machine-readable artifacts and run a cheap diff sanity check before committing review updates:

```bash
python3 - <<'PY'
import json, yaml
json.load(open('_bmad/state.json'))
yaml.safe_load(open('_bmad/sprint-status.yaml'))
print('artifact parse ok')
PY
git diff --check
```

## Verdict nuance

- If `corepack pnpm ...` now works and lint/typecheck/test/Prisma validation pass, the previous package-manager blocker is resolved.
- If lint has migrated from `next lint` to `eslint . --max-warnings=0`, verify the script really runs through Corepack pnpm.
- Do **not** overclaim "Next ESLint plugin/rule coverage" just because ESLint CLI passes. `next build` may still warn: `The Next.js plugin was not detected in your ESLint configuration`.
  - Treat this as a non-blocking carry-forward note for a scaffold story when the story only required a working lint script.
  - Treat it as a blocker only when the story explicitly required Next-specific ESLint plugin/rules or the missing rule coverage hides a story-critical issue.
- `corepack pnpm install --frozen-lockfile` is useful in the fresh review because a package-manager correction can leave a lockfile/package metadata mismatch that lint/typecheck/test alone may not expose.

## Artifact reconciliation pattern

For a passing focused scaffold re-review:

- Append the fresh review under the story's `## Review Findings` section.
- Move the story/state/sprint status to `review_passed_with_notes` / `PASS_WITH_NOTES` when carry-forward notes remain.
- Point evidence to the fresh review anchor, not the correction/dev record anchor.
- Set the next workflow to `bmad-state-check` for progression/next-story selection, not back to `bmad-code-review`.
- Update continuation docs concisely: current status, verdict, validation commands, carry-forward notes, and next workflow.
