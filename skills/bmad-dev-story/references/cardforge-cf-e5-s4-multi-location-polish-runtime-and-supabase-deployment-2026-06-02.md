# CF-E5-S4 — Multi-Location Polish, Runtime QA, and Supabase Deployment (2026-06-02)

Story-level round-2 evidence for the `bmad-dev-story` correction that
closed the 2026-06-02 BLOCKED review.

## Round-1 blockers and how round 2 closed them

1. **Server-side bucket-total invariant was missing.** The `replaceBucketsForCardItem` helper in `src/lib/db/owner-scope.ts` selected only `{ id: true }` from `CardItem`, never read `CardItem.quantity`, and could persist mismatched or empty buckets on a positive-quantity card.

   Round-2 fix:
   - Select `card.quantity` too: `select: { id: true, quantity: true }`.
   - Compute `submittedTotal = buckets.reduce((s, b) => s + b.quantity, 0)`.
   - Reject with `Bucket total (${submittedTotal}) does not match card quantity (${card.quantity})` BEFORE opening the `$transaction`. This is the critical ordering — the atomic transaction is the dangerous primitive and must not run if the invariant is already broken.
   - 6 new focused tests in `tests/unit/cf-e5-s4-multi-location-polish.test.ts` (13 → 19): empty list on positive card, underflow, overflow, exact sum, empty list on qty=0, and "rejected before any DB write" (the last asserts the guard runs before `$transaction`).
   - Updated the existing CF-E5-S3 atomicity test in `tests/unit/cf-e5-s3-multi-location-stock.test.ts` to mock `prisma.cardItem.findFirst` returning `quantity: 5` (see SKILL.md pitfall "enriching a repo helper to read a previously-unread column breaks prior round's focused tests' mock surface").

2. **Story-required authenticated runtime smoke was incomplete.** Round 1 only proved dev server compile + `/login` render + unauthenticated `/inventory` redirect.

   Round-2 fix:
   - New `tests/e2e/cf-e5-s4-runtime-smoke.spec.ts` (7 tests A–G) signing in as `reagulus.dev@gmail.com` (the user James provided, owner_id 9) and exercising the full multi-location surface.
   - Deterministic seed: 4 cards + 5 buckets for owner 9. Invariant `sum(bucket.quantity) == cardItem.quantity` verified for all four rows.
   - 7/7 pass in 1m36s against a live Supabase-backed dev server.

## Why the invariant lives in the repo helper, not the action

The new guard sits next to `applyMergeStockForOwner`'s existing invariant (which is enforced inside its own `$transaction`). The action layer is reduced to a thin schema-validation + trim/normalize pass that hands off to the helper. This is the "narrower repo helper when the client must NOT supply a calculated value" pattern (see SKILL.md Reusable patterns): the boundary is the authoritative guard, and the client cannot bypass it.

## Authenticated runtime smoke environment quirks

1. **React hydration in dev mode takes 1–3s.** `page.locator(...).fill()` on a controlled input before hydration writes to the DOM but leaves React state empty; the form then falls back to native HTML submission, bypassing the `onSubmit` handler. The login helper waits for the `__reactProps` key and uses the native React-aware value setter (`Object.getOwnPropertyDescriptor(proto, "value")?.set`) — full template at `~/.hermes/skills/playwright-runtime-smoke/templates/react-controlled-input-login.ts`.

2. **Supabase per-IP rate limit hits on tight test loops.** The login helper retries 3 times with exponential backoff on HTTP 429.

3. **Modals without `role="dialog"`** — `MultiBucketEditor` and `CardItemEditDialog` are raw `<div>` modals, not the shared `Dialog` component. The spec anchors on the modal's heading text and scopes subsequent `locator(...)` calls to the wrapping `div` via `has: page.getByText(/.../)`.

4. **Prisma pool `connection_limit=1`.** Parallel E2E contexts exhaust the pool. `test.describe.configure({ mode: "serial" })` keeps everything in one browser context.

5. **Stale dev-server processes hold port 3000** across long sessions. `ss -tlnp | grep :3000` + `kill <pid>` is the first step in any E2E setup.

## Build / lint notes

- The lint gate uses `--max-warnings=0`. Initial E2E spec had two `@typescript-eslint/no-explicit-any` warnings on the React-aware setter helper; fix was to type as `HTMLInputElement | null` and `Record<string, unknown>`.
- `git diff --check` reports "new blank line at EOF" on `CONTINUE-HERE.md` after a `write_file` round trip; strip the trailing blank line.
- The Next.js ESLint-plugin "plugin not detected" warning is intentionally NOT fixed (per the project's `eslint.config.mjs`). Do not "fix" it.
- The `turbopack.root should be absolute` warning is fixed via `path.resolve(process.cwd())` in `next.config.ts`.

## Artifact reconciliation order (round 2)

1. `_bmad/state.json` — `workflow_status: review_blocked` → `implemented_not_reviewed`; `active_workflow: bmad-dev-story` → `bmad-code-review`; blockers cleared; new state_check note appended.
2. `_bmad/sprint-status.yaml` — story status, validation_summary, review_notes, carry_forward_concerns updated.
3. `CONTINUE-HERE.md` — Current Status section rewritten; old "Previous Story" entry for CF-E5-S4 replaced with a round-2 entry.
4. Story artifact — new "Dev Agent Record (round 2 — correction)" appended; round-1 record preserved.

## Files changed in round 2

Modified:
- `src/lib/db/owner-scope.ts` (new invariant)
- `src/lib/actions/inventory.actions.ts` (clarified docstring)
- `tests/unit/cf-e5-s4-multi-location-polish.test.ts` (+6 tests; mocked `$transaction` added)
- `tests/unit/cf-e5-s3-multi-location-stock.test.ts` (mock now returns `quantity: 5`)
- `_bmad/artifacts/stories/CF-E5-S4-multi-location-polish-runtime-and-supabase-deployment.md`
- `_bmad/state.json`
- `_bmad/sprint-status.yaml`
- `CONTINUE-HERE.md`

New:
- `tests/e2e/cf-e5-s4-runtime-smoke.spec.ts`
- `_bmad/artifacts/evidence/CF-E5-S4/runtime-smoke.md`

## Validation

- `corepack pnpm run typecheck` — PASS
- `corepack pnpm run lint` — PASS (0 warnings)
- `corepack pnpm test` — 397/397 across 26 files (one pre-existing unrelated `csv-import-large-batch` ENOENT failure is unchanged from main; confirmed via `git stash` + rerun + pop)
- `corepack pnpm run build` — PASS
- `corepack pnpm exec prisma validate` — PASS (no schema change)
- `git diff --check` — PASS (after stripping trailing blank line on `CONTINUE-HERE.md`)
- `corepack pnpm exec playwright test tests/e2e/cf-e5-s4-runtime-smoke.spec.ts` — 7/7 in 1m36s

## Next workflow

Fresh `bmad-code-review` for CF-E5-S4 (round 2).
