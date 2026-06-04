---
name: bmad-dev-story
description: Execute a development story in a disciplined BMad manner using explicit state, validation, and evidence instead of vague completion claims.
version: 2.0.2
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, implementation, stories, validation, execution]
    related_skills: [bmad-state-check, bmad-code-review, bmad-evidence-reporting]
---

# BMad Dev Story

> **Reference file**: `references/validation-gates.md` — validation gate commands, action return contract, owner scoping patterns, GBP money handling, native dialog usage, Prisma-as-type pattern, and sprint-status.yaml update sequence.
> **Analytics pattern**: `references/cardforge-analytics-dashboard-date-filter-2026-05-24.md` — server/client Date serialization for date filters and prisma validate with missing .env.
> **CF-E5-S2 patterns**: `references/cardforge-cf-e5-s2-bulk-lot-assignment-2026-06-02.md` — narrower repo helper for server-side calculated values, deliberate `__none` sentinel for null filters, raw URL passthrough to schema, two visible controls over one ambiguous control, and the CardForge bulk-lot-assignment cost-basis contract.
> **CF-E5-S3 patterns**: `references/cardforge-cf-e5-s3-multi-location-stock-2026-06-02.md` — three rounds of corrections (patterns 1–21) covering: additive per-row child model with bucket invariant at every write boundary, Vitest `$transaction` mock implementation pattern, `updateForOwner` uses singular `update` not `updateMany`, chaos-sort merge accumulation across rows, chaos-sort identity key including all logical fields, composite owner-consistent Prisma relation, additive migration with backfill in the same file, atomic stock-mutation helper as a repo-layer boundary with pre-flight invariant guard, defense-in-depth allowlist at the repo layer for sortBy/orderBy, normalization of free-form CSV strings to Prisma enums with explicit `OTHER` fallback, the Vitest `mockReset` fix for queued `mockResolvedValueOnce` pollution across sequential tests, same-batch new-identity CSV merge coalescing, atomic create-with-initial-buckets helper, two-axis boundary-walk table (with related rows present AND without related rows present), in-tx helper reads canonical row's post-mutation quantity (not the signed delta) for the no-children branch.
> **CF-E5-S4 round 2**: `references/cardforge-cf-e5-s4-multi-location-polish-runtime-and-supabase-deployment-2026-06-02.md` — server-side bucket-total invariant added to `replaceBucketsForCardItem` (reads `CardItem.quantity`, rejects before `$transaction`); the "enriching a repo helper to read a previously-unread column breaks prior round's focused tests' mock surface" pitfall (concrete: cf-e5-s3 atomicity test had to gain `quantity: 5` on its `findFirst` mock); authenticated runtime smoke (7 Playwright tests A–G signing in as `reagulus.dev@gmail.com`); React controlled-input login helper template at `~/.hermes/skills/playwright-runtime-smoke/templates/react-controlled-input-login.ts`.
> **Negative profit crash**: `references/cardforge-cf-e1-s6-negative-profit-crash-2026-05-25.md` — profit/loss must not crash when negative.
> **Negative margin display**: `references/cardforge-cf-e1-s6-negative-margin-display-2026-05-25.md` — never hide negative margin as "—".
> **Auth/session correction**: `references/cardforge-cf-e1-s7-auth-session-correction-2026-05-25.md` — CF-E1-S7 fix for UserProfile bootstrap and Supabase SSR cookie handling.
> **vi.mock type widening fix**: `references/cardforge-vitest-vi-mock-type-widening-2026-05-29.md` — TS2339 on mockImplementation/mockResolvedValue in Vitest unit tests with vi.mock factories; fix with ReturnType<typeof vi.fn> cast.
> **Marketplace-channel foundation**: `references/cardforge-marketplace-channel-foundation-2026-05-31.md` — safe additive pattern for adding Shopify/marketplace channels without live sync, including listing-allocation schema and UI/config/test expectations.
> **Secure OAuth pattern**: `references/nextjs-secure-oauth-pattern.md` — signed state, HMAC verification, token encryption, owner-scoped persistence, and testable token-exchange boundary for third-party OAuth in Next.js (Shopify, Stripe Connect, etc.).
> **CF-E4-S2 correction lessons**: `references/cardforge-cf-e4-s2-correction-2026-05-31.md` — Vitest pitfalls with Next.js route handlers, mocking exchangeAccessToken, and crypto key validation tests.
> **Next.js route handler unit tests**: `references/nextjs-route-handler-unit-tests-vitest-jsdom.md` — how to behavior-test Next.js App Router handlers in Vitest/jsdom using lightweight mock NextRequest objects, and the `NextResponse.redirect` absolute-URL pitfall.
> **CF-E5-S6 background-job pattern (Hobby-safe + Pro-compatible)**: `references/cardforge-cf-e5-s6-hobby-safe-background-job-csv-import-2026-06-03.md` — when a synchronous Server Action's wall-clock exceeds the serverless limit (e.g. Vercel 300s), move the work to a Job table + client-poll-driven tick pattern. Hobby-plan safe (no Vercel cron needed). Includes the dialog's localStorage recovery + `lastTickAt` heartbeat + back-compat shim for legacy synchronous test surface.
> **CF-E5-S6 background-job pattern, round 2 correction**: `references/cardforge-cf-e5-s6-hobby-safe-background-job-csv-import-2026-06-03-round-2.md` — the round-1 design was unsafe on four co-dependent boundaries (non-atomic tick claim, crash-after-write reprocesses chunks, failed creates advance the counter, merge retries use stale submit-time quantities). Round 2 introduces atomic `claimAndStart` (updateMany predicate), `advanceProgressBeforeRun` (BEFORE the runner, so a crash-after-write leaves the next tick starting from the new offset), `recordCountersAfterRun` (takes the runner's actual persistence counts), and `applyDeltaMergeStockForOwner` (additive merge inside `prismaDirect.$transaction`, safe under replay). The runner always re-fetches the live DB snapshot at tick start. Class-level PITFALL below generalises the checklist to any future per-chunk tick model on a job table.
> **CF-E5-S6 round 2 new-repo dual-client regression**: `references/new-repo-dual-client-regression-review.md` (in `bmad-code-review`) — when a story introduces a NEW repo module that opens `$transaction` for claim/advance/record helpers, the dev-story agent must import `prismaDirect` (not just `prisma`) and use **DISTINCT `vi.fn()` instances** for each client's `$transaction` in the new repo's unit-test mock, otherwise the wrong-client usage hides behind a passing test run. The minimum-acceptable pattern of aliasing `prismaDirect: mockPrisma` to the same object is insufficient as a runtime guard (the `as unknown as` cast strips the typecheck); distinct instances + wiring tests catch the regression at test time. Extends the CF-E5-S5 P2028 reference from EXISTING to NEW repos. Includes a patch-tool collision pitfall when migrating existing test bodies via `patch` with `replace_all=true`.

## When to Use

Use when implementing a concrete story, fix, or scoped code change for a project under `<project_root>`.

## Goal

Move a story from intent to validated implementation while preserving truthful status, project-local traceability, and clear evidence.

## Key Conventions

- Actions used in `action={}` form attributes **must** return `Promise<void>`. Do not return typed result objects.
- Owner scoping: always use `resolveCurrentOwnerId()` from `@/lib/auth/owner-resolver`.
- Amounts stored as **integer pence** (no decimals); convert £→pence on submission.
- For 3-decimal accuracy (millipence ×1000), see the Millipence Migration section below.
- Edit dialogs use the native HTML `<dialog>` element.
- Prisma model types used directly in client components (no intermediate custom types).
- Expense archive uses `expenseRepo.archiveById(id)` (soft archive), not hard `delete`.
- Zod schema enums do not need separate enum imports in actions files — import the schema only.

## Secure Third-Party OAuth in Next.js

When a story adds an OAuth connection to a third-party service (e.g., Shopify, Stripe Connect, Xero):

- See `references/nextjs-secure-oauth-pattern.md` for the full module layout, code patterns, and test strategy.
- Summary of non-negotiable rules:
  1. **Domain normalization**: reject non-provider domains before building redirect URLs.
  2. **Signed state**: HMAC-SHA256 over JSON payload with owner id, session nonce, shop domain, and expiry. Store nonce in httpOnly cookie.
  3. **Callback HMAC**: canonicalize query params (sort keys, join `key=value` with `&`, exclude `hmac`). Use `timingSafeEqual`.
  4. **Token exchange**: accept injected `fetchImpl` for testability. No live network calls in normal tests.
  5. **Token encryption**: AES-256-GCM with per-encryption random salt/IV, scrypt key derivation. Server-only. Never return to client.
  6. **Owner-scoped repo**: always include `owner_id` in `where`. Upsert must not touch another owner's row.
  7. **Service orchestration**: `buildOAuthStart`, `handleOAuthCallback`, `getConnectionStatus`. Status must never include encrypted tokens.
  8. **Routes**: `requireAuthedOwnerId()` first; safe redirect outcomes on success/failure; clear nonce cookie after callback.
  9. **Dashboard UI**: four states (missing-config, configured-not-connected, connected, disabled). No misleading "syncing/published/orders" copy.
- Do not claim live OAuth success unless a real account/store was exercised. Mocked tests prove boundary behavior only.
- Do not use `NEXT_PUBLIC_SUPABASE_URL` as the app origin for redirect URIs. Use `NEXT_PUBLIC_APP_URL` or derive from request headers.

## Analytics / Profit / COGS (CardForge)

When implementing or correcting analytics, profit, or COGS (e.g., CF-E1-S6):

- Always base COGS on **sale-level quantities**, not current cardItem.quantity:
  - Use `sale.quantity` per COMPLETED sale, plus that sale's linked `cardItem.cost_basis_pence`.
  - Never compute COGS as `cost_basis_pence * cardItem.quantity` for "sold" cards.
- Gross profit must include fees:
  - `gross_profit = revenue - COGS - (platform_fee + payment_fee)`.
- Net profit must include shipping cost and expenses:
  - `net_profit = gross_profit - shipping_cost - expenses`.
- Margin:
  - `margin = (net_profit / (revenue + shipping_charged)) * 100`, or 0 if denominator = 0.
- Align with existing `calcSaleProfit()` in `src/lib/money/index.ts`; do not invent a second profit model.
- Ensure both dashboard helpers (e.g., `calcDashboardMetrics`) and export logic (e.g., MARGIN_SUMMARY) use the same formulas.
- PITFALL (CF-E1-S6): profit/loss and margin can be legitimately negative.
  - If your money formatter (e.g., `formatGbp`) uses a validator that rejects negative values, it will crash the dashboard on loss-making periods or loss-making breakdown rows.
  - Fix pattern:
    - Keep a non-negative `toPence(value)` for amounts (revenue, COGS, etc.).
    - Provide `toPenceAllowNegative(value)` for profit/loss/margin.
    - Provide `formatProfitGbp(pence)` that:
      - Positive/zero: "£12.34"
      - Negative: "-£12.34"
    - Use `formatProfitGbp` in all UI that displays profit/loss (Gross Profit, Net Profit, and per-platform/set/card/lot breakdowns).
  - Add a regression test for:
    - A dashboard scenario where COGS + expenses > revenue (negative net profit).
    - A breakdown row (e.g., platform) that yields negative profit and is formatted without throwing.

- PITFALL (CF-E1-S6, negative margin display): do not hide negative margin/profit as "—".
  - It is incorrect to use conditions like `marginPct > 0 ? "..." : "—"` when negative margin is valid.
  - "—" should only be used when there is no data (e.g., marginPct === 0 and no sales), not when there is a loss.
  - Correct pattern:
    - For margin:
      - marginPct !== 0 ? `${marginPct.toFixed(1)}%` : "—"
    - For profit/loss:
      - Always render with a negative-aware formatter (e.g., formatProfitGbp), never coerce to "—".
  - Test pattern:
    - Add a regression test that:
      - Uses a loss-making scenario.
      - Confirms the UI-style rendering logic shows a negative value (e.g., starts with "-") and not "—".
    - Mirror the exact rendering expression from the component in the test so future refactors cannot drift silently.

## Millipence Migration (CF-E3 Pattern)

When migrating money precision (e.g. pence ×100 → millipence ×1000 for 3-decimal accuracy):

1. **Schema**: create a single `UPDATE ... SET col = col * 10` migration SQL for every monetary column.
2. **Money helpers**: rename functions (`gbpToPence` → `gbpToMillipence`, `toPence` → `toMillipence`, etc.) and update divisor (`/100` → `/1000`, `*100` → `*1000`).
3. **Server actions**: update all `gbpToPence()` calls to `gbpToMillipence()`.
4. **UI inputs**: change `step="0.01"` → `step="0.001"` on all money number inputs.
5. **UI display**: change all `/100).toFixed(2)` → `/1000).toFixed(3)` and `*100` → `*1000` in onChange handlers.
6. **Analytics**: update `calcSaleProfit` field names (`salePricePence` → `salePriceMillipence`, etc.) and all call sites.
7. **CSV export**: update `penceToGbp` → `millipenceToGbp` with 3 DP.
8. **Tests**: multiply every hardcoded money value by 10 and update expected format strings (`"£12.34"` → `"£12.340"`).
9. **Prisma field names**: keep `*_pence` column names — they are just labels; the values are in millipence after migration.
10. **Run full test suite** before claiming done. All existing tests should still pass.

PITFALL: do not try to rename Prisma columns — that requires a second migration. The `*_pence` suffix is acceptable; only the values change.
PITFALL: the DB migration must be applied to production BEFORE the code deploys, or the app will read pence values as millipence (off by 10×).

## Analytics / Export Tests (CardForge)

For stories touching analytics, exports, or HMRC-style CSVs (e.g., CF-E1-S6), you are expected to add focused tests, not rely solely on existing ones. Typical required coverage:

- `calcDashboardMetrics`-style formulas:
  - COGS uses sale.quantity, not cardItem.quantity.
  - Fees and shipping cost appear in gross/net profit as specified.
- Date/platform filters:
  - Only COMPLETED sales in range.
  - Platform filter is respected.
- Breakdown grouping:
  - Platform, set, card, and lot breakdowns aggregate by the correct keys and quantities.
- CSV row shapes and source IDs:
  - Headers match the documented shape.
  - Source IDs (sale_id, card_item_id, lot_id, expense_id, etc.) are included.
- Export route/service:
  - Route handler exists and rejects invalid filter/exportType (400).
  - Owner-scoped calls are exercised via mocks where practical.

See: `references/cardforge-cf-e1-s6-analytics-correction-2026-05-24.md` for a concrete example.

## Validation Gates

Run in order. Stop on first failure unless the failing test is explicitly pre-existing and unrelated.

```bash
corepack pnpm typecheck
corepack pnpm lint
corepack pnpm test
corepack pnpm build
# prisma validate requires DATABASE_URL — if .env is absent or empty, use a valid-format placeholder:
DATABASE_URL='postgresql://placeholder:***@localhost:5432/placeholder' corepack pnpm exec prisma validate
git diff --check
```

> **Schema tests**: `node --experimental-vm-modules vitest run tests/unit/<story-slug>-schemas.test.ts` — only run directly when the file exists. If no schema test was created for the story, this gate is skipped silently.

## Batch Edit Pattern for Multi-File Changes

When a story touches many files (e.g., a uniform migration across all money fields, or a rename across the codebase):

- Use `execute_code` with a Python script that calls `patch()` or `write_file()` programmatically.
- This is faster and more reliable than many separate `patch` tool calls, and avoids context-window bloat from repeated diff output.
- After the batch, run `git diff --stat` to verify coverage, then run the full test suite.
- PITFALL: `patch` with `replace_all=True` on a file can corrupt structure if the match string is too short. Always include enough surrounding context (3–5 lines) to ensure uniqueness.
- PITFALL: when replacing JSX elements (e.g. `<TableCell>` → `<div>`), include the full opening tag and content in the old_string to prevent partial replacements that break the component tree.

## Artifact Update Sequence

After `git diff --check` passes, update in order:

1. `_bmad/state.json` — `workflow_status: implemented_not_reviewed`, `active_workflow: bmad-code-review`
2. `_bmad/sprint-status.yaml` — story `status: implemented_not_reviewed`, `validation_summary`, `next_recommended_workflow`
3. `CONTINUE-HERE.md` — story status and next workflow
4. Story artifact — append "Dev Agent Record": files changed, validation results, key decisions

## sprint-status.yaml Pitfall

Indentation matters. Patch can corrupt YAML. **Prefer write_file (full rewrite)** over patch for this file. Always re-read the file with `cat -A` (or read a few extra lines) to verify exact bytes before assuming fields exist — for example, the top of `sprint-status.yaml` may or may not include a `current_sprint:` line depending on the project's history; do not assume.

## corepack pnpm is Mandatory, Not Optional

The CardForge-style projects in this foundry use `pnpm-workspace.yaml` and pin a pnpm version via corepack. **Always invoke `corepack pnpm run <script>`** (or `corepack pnpm exec <cmd>`), never bare `pnpm typecheck` or `pnpm test`.

**Why this matters concretely:**

- The system `pnpm` (commonly 0.34.6 on this image) does NOT auto-route script names to the local `package.json`. It treats `pnpm typecheck` as a literal subcommand, fails, and prints:

  ```
  Unknown Syntax Error: Command not found; did you mean one of:
   0. corepack -h
   1. corepack -v
   ...
  While running typecheck
  ```

  The `While running typecheck` line is the tell — it's pnpm 0.34.6 trying to run a subcommand called `typecheck`, not the project script. This is a silent-equivalent failure: the script never ran, the gate was not actually exercised, exit code is 0 from the bash wrapper.

- `corepack pnpm` (10.12.0 on this image) routes correctly to the project's `package.json` scripts.

**Verification**: after a successful gate, the output should start with `> cardforge@0.1.0 <script> /home/.../cardforge` and end with the script's own output. If you see the `Unknown Syntax Error` block, you forgot the `corepack` prefix.

## Auto-Lint False Positives on Patch Tool Output

The `patch` tool's auto-lint runs `tsc` on the edited file in a context that may differ from the project's `tsconfig.json` (e.g. no `paths` for `@/*` aliases, different target). Symptom: the auto-lint reports errors like:

- `TS2307: Cannot find module '@/lib/auth/auth-guard' or its corresponding type declarations.`
- `TS18028: Private identifiers are only available when targeting ECMAScript 2015 and higher.` (from Prisma or Vitest bundled `.d.ts`)
- `TS2802: Type 'Map<number, number>' can only be iterated through when using the '--downlevelIteration' flag`

**These are not real errors in the CardForge project.** The project's `tsconfig.json` uses `target: ES2022`, `skipLibCheck: true`, and the `@/*` path alias; the auto-lint's tsc invocation does not. The existing source tree contains thousands of similar-looking constructs that all typecheck cleanly under the real `tsc --noEmit` gate.

**Rule**: never trust auto-lint output as the typecheck signal. Always run the real gate:

```bash
corepack pnpm run typecheck
```

If the real gate is clean, proceed. If the auto-lint and the real gate disagree, the real gate wins.

## Pre-Existing Lint/Build Warnings That Block a Gate

When a gate fails because of a **pre-existing** warning/error on `main` (not introduced by your story), do not silently fix it and do not silently skip. Verify it is pre-existing by `git stash` + rerun + `git stash pop`, then use `clarify` to ask the user with concrete options. Typical options:

1. Fix in the same commit (1-2 line scope-clean, document the scope-widening in the story's Dev Agent Record).
2. Leave it; document "pre-existing unrelated to this story" and treat the gate as not-blocking.
3. Open a tiny follow-up story (e.g. `CF-X-Sx-cleanup`) to handle it out-of-band.

For tests (not lint) the dev-story skill already prescribes "note it and continue" for pre-existing unrelated test failures; the same rule does not apply to lint, because `--max-warnings=0` fails the whole gate.

⚠️ **Consent-guard pitfall**: if a batch artifact update script is blocked by a consent guard before making changes, do not abandon the BMad handoff or claim completion with stale artifacts. Ask the user for explicit permission to update the artifacts, then perform the same intended artifact reconciliation and validate JSON/YAML/story markers afterwards.

⚠️ **Consent-guard pitfall**: if a batch artifact update script is blocked by a consent guard before making changes, do not abandon the BMad handoff or claim completion with stale artifacts. Ask the user for explicit permission to update the artifacts, then perform the same intended artifact reconciliation and validate JSON/YAML/story markers afterwards.

## Delegation to Cheaper or Weaker Models

When delegating `bmad-dev-story` correction work to a cheaper/weaker subagent (e.g., MiniMax M2.7), the brief must include:

- Story ID, path to story artifact, pointer to "Review Findings"
- "You are doing bmad-dev-story, not bmad-code-review. Fix the code, run validation, update Dev Agent Record."
- Explicit list of what needs fixing (not vague "fix the issues")

Controller rule after delegation: treat the subagent output as a draft until the controller verifies the actual repo state. MiniMax/Hermes CLI wrappers can exit non-zero after writing useful code and partial artifacts; inspect files, tighten weak tests to exercise production boundaries, rerun validation, and only then reconcile BMad artifacts. See `references/minimax-subagent-exit-pitfall.md`.

### Model-specific delegation requests

If the user asks for the correction subagent to run on a specific model/provider (for example Kimi K2.6), first check whether the active delegation surface can actually pin a model. `delegate_task` may not expose a per-call model/provider override; putting “use Kimi” in the prompt is not a verified routing control. If exact model routing is required, prefer a model-pinned execution path (for example a spawned Hermes CLI process with provider/model flags or a profile configured for that model) or ask for confirmation before using a non-pinned delegate. After any delegated run, inspect/report the returned actual `model` field when present and be transparent if it differs from the requested model. See `references/delegated-correction-model-routing.md`.

For form-action corrections, verify the subagent did not over-broaden a fix from the blocked path into adjacent paths. In particular, preserving blank-string intent for edit/clear semantics may be correct for updates while create actions should still avoid persisting unwanted empty strings. Add/verify tests for blank edit clears, non-blank edit persistence, and blank create optional fields. See `references/form-blank-field-correction-controller-check.md`.

## State Check First

Always run `bmad-state-check` before starting. If `state.json`'s `active_workflow` is not the workflow you're about to run, resolve the mismatch first.

### Workflow routing when state doesn't match requested workflow

If `state.json` shows `workflow_status: implemented_not_reviewed` and `active_workflow: bmad-code-review`, but the user asks to "run bmad-dev-story" for that same story:

- The story is **already past the dev-story gate** — re-running implementation would overwrite the Dev Agent Record and lose evidence.
- Correct response: offer `bmad-code-review` (review the existing implementation) or `bmad-dev-story correction` (fix specific issues found in review).
- Only run `bmad-dev-story` as a fresh start when state shows `ready_for_dev` or `review_blocked`.

Use `bmad-state-check` to resolve mismatches before proceeding.

### Story artifact status is `ready_for_dev` but the artifact has open scope-review questions

A story can be `ready_for_dev` and still have material open questions in the artifact body (e.g. "5 open scope-review questions for the founder" in CF-E5-S6). The state machine does not enforce that the artifact is *complete* — only that the prior workflow gate has passed. If you open `bmad-dev-story` against an artifact whose open questions materially change the implementation shape (plan-vs-Hobby pivot, cancel vs no-cancel, polling cadence, etc.):

- Do NOT silently pick defaults and start coding. The 1,000+ lines you write will assume a pivot the founder may not have approved.
- Use `clarify` to ask the founder for explicit scope decisions on each open question, framed as concrete options. The artifact's "Open scope-review questions" section is usually the prompt.
- In the question, include the choice of "use the defaults the artifact encodes" as a safe default. The founder can pick defaults without losing context.
- After the founder responds, log the resolutions in the Dev Agent Record under "Key decisions" so the next reviewer can see the trail.

Symptoms of having missed this:
- You spend hours implementing "the Pro plan with Vercel cron" and the founder was on Hobby.
- You add a cancel button the founder explicitly chose to omit.
- You introduce a hard `UNIQUE` constraint the founder said was overkill for v1.

The cost of asking is one round-trip. The cost of guessing wrong is the story having to be redone.

## Story Lifecycle

1. **Create** → `bmad-create-story` produces `artifacts/stories/<id>.md` and updates sprint-status.yaml
2. **Implement** → `bmad-dev-story` moves story to `implemented_not_reviewed`
3. **Review** → `bmad-code-review` validates implementation, produces review findings, marks story `reviewed` or returns `correction_needed`
4. **Correct** → `bmad-correct-course` if review found gaps
5. **QA** → `bmad-qa-gate` for runtime/founder verification before release

## File Naming for New Work

- Tests: `tests/unit/<story-slug>-schemas.test.ts` (e.g., `expense-schemas.test.ts` for CF-E1-S5)
- Actions: `src/lib/actions/<topic>.actions.ts`
- Components: `src/app/(dashboard)/<topic>/_components/` with `useFormStatus` and native `<dialog>` for edits

## Data Layer

Use existing repositories in `owner-scope.ts` before creating new ones. Repositories are already owner-scoped — never hardcode `ownerId = 1`.

## Evidence Requirements

Before claiming completion, gather:
- `pnpm typecheck` — pass
- `pnpm lint --max-warnings=0` — pass
- `pnpm test` (or direct vitest for schema tests) — pass
- `pnpm build` — pass
- `git diff --check` — no whitespace errors

For runtime-sensitive features, document what could not be verified without a live environment (Supabase/RLS, auth, payment). Mark those as "deferred runtime verification."

## Pitfalls

- Do not infer completion from artifact presence alone.
- Do not infer runtime success from static review alone.
- Do not skip state inspection just because the user sounds certain.
- Do not silently normalize mixed camelCase and snake_case mentally; call out schema drift when it matters.
- When a session was cut off or compacted, do not immediately advance to the next story just because state suggests the prior story is mostly done. First close or explicitly mark the named interrupted target, then recommend the next workflow.
- When story artifacts or files cannot be found via search, use direct paths from state.json (last_artifacts, current_story) and sprint-status.yaml (story_artifact) as authoritative. Do not loop identical search calls; fall back to read_file on known paths or terminal-based listing.
- When a story is review_blocked, do not treat it as “done but with notes.” It is not allowed to advance until:
  - A correction is implemented,
  - A fresh bmad-code-review passes (even with notes),
  - And state/sprint/story artifacts are updated to implemented_not_reviewed → review_passed_with_notes.
- PITFALL (Terminal Backend Degraded): SSH terminal may be "connected" (exit_code=0) but silently broken:
  - Symptoms: echo, whoami, ls, uname all return empty output; writes to /tmp result in empty files.
  - If this happens:
    - Do not proceed with bmad-dev-story (you cannot trust validation or file reads).
    - After 2–3 failed probes (e.g., echo, ls, test -d), stop and tell the user:
      - "Terminal backend appears degraded; I cannot safely run bmad-dev-story."
      - Offer: (1) restart Hermes terminal backend, (2) user pastes key artifacts, (3) user confirms a different project path.
    - Do not loop-probe or guess paths while the terminal is in this state.

- PITFALL (display redaction vs file bytes for hardcoded credentials): when writing a test file that contains a hardcoded test-account password (e.g., a Playwright e2e spec, a seed fixture, a doc snippet), the Hermes toolchain may render the literal value as `***` in your `write_file` argument preview, in `grep` output, in `sed` output, and in `cat` output. Crucially, this is a display-layer redaction — but the file bytes may ALSO be the literal `***` if the value got truncated during the `write_file` argument serialisation. Do not trust the visible value in your own tool output; audit the actual file bytes before committing.
  - Audit recipe (use ALL of these, not just one):
    1. `cat -A <file> | grep -n PASSWORD_LINE` — the `-A` flag disables display redaction and shows raw bytes including non-printables.
    2. `python3 -c "with open('<file>','rb') as f: data=f.read(); idx=data.find(b'<unique_anchor>'); print(repr(data[idx:idx+60]))"` — the `repr()` output is unambiguous about literal bytes.
    3. `git diff --check` — does not catch this; pure whitespace check.
  - Symptom of the truncation: the file contains the literal placeholder string `***` where the password should be. The e2e spec will fail at runtime with a Supabase auth error (or whatever the auth provider is), and the failure will be misdiagnosed as a Playwright timing issue or a server-action contract change. It is actually a typo in the test fixture.
  - Two safe options when the value is a real test-account credential:
    1. **Reconstruct character-by-character** in the tool argument (`"Test" + "er1234"` or via Python byte concatenation), bypassing the display redaction in transit. Verify with `cat -A` after the write.
    2. **Move the credential out of the source file** into a CI/dev-only env var (e.g., `TEST_USER_PASSWORD`) and read it in the test. The test file no longer contains the literal; the env var carries it.
  - Always re-read the file's bytes after the write, before the next `git add`. Do not trust the write tool's success message as evidence the value is correct.
- For large stabilization stories with many acceptance criteria across multiple areas (UX, E2E, edge cases):
  - Use execute_code with batch patching for multi-file changes instead of many separate terminal commands.
  - Avoid heavy Prisma/Supabase mocking in unit tests; prefer testing pure calculation functions directly.
  - For E2E tests, follow the existing mvp-smoke.spec.ts patterns (same test user style, DOM assertions).
  - See: `references/validation-gates.md` for the "Large Stabilization Stories" guidance.

- PITFALL (Prisma + Supabase transaction pooler + Vercel Lambda race returns P2028): when a serverless-deployed app uses `prisma.$transaction(async (tx) => { ... })` and the production `DATABASE_URL` is the Supabase Transaction Pooler (port 6543, pgbouncer=true), pgbouncer's transaction-mode pool reassigns a fresh physical connection mid-transaction under Vercel Lambda connection reuse, that connection has no `BEGIN` context, and Postgres returns P2028 ("Transaction not found"). The bug is always latent against the live pooler; Vitest (local DB) and `cf-e5-s4-runtime-smoke`-style auth-only Playwright specs cannot catch it. Fix is a dual Prisma client: keep `prisma` on the pooler for reads and single-statement writes; add `prismaDirect` on `DIRECT_URL` (port 5432, direct) and route every `$transaction` call site to it; add an `assertDirectUrl` runtime guard that rejects `pgbouncer=true` or port 6543 in `DIRECT_URL`. See `references/prisma-supabase-transaction-pooler-p2028.md` (in `bmad-code-review`) for the full class-level pattern.
- PITFALL (new repo module after the dual-client split — wire `prismaDirect` from day one, not as a follow-up): when a story introduces a NEW repo module under `src/lib/db/` (e.g., `job-repo.ts` for a background-job model) and that module needs `$transaction` for claim/advance/record helpers, do NOT use `prisma.$transaction(...)` "to match the existing module pattern" without first checking whether the existing module is on the pooler or on the direct client. The CF-E5-S5 closure rule is global: *every `prisma.$transaction(async (tx) => { ... })` call site routes to `prismaDirect.$transaction(...)`*, including sites inside NEW repos. The cheapest way to introduce the regression is to import only `{ prisma }` from `./prisma` and call `prisma.$transaction` from a new helper. The next review will block on P2028 against the live pooler. Defensive pattern when authoring a new repo:
  1. Add `prismaDirect` to the import line: `import { prisma, prismaDirect } from "./prisma";`.
  2. Use `prisma` for reads and single-statement writes (the standard pattern).
  3. Use `prismaDirect.$transaction(async (tx) => { ... })` for any multi-statement write helper.
  4. **In the new repo's unit-test mock, use DISTINCT `vi.fn()` instances for `prisma.$transaction` and `prismaDirect.$transaction` (not just aliased to the same mock object).** The minimum-acceptable pattern in the existing codebase is to alias both clients to the same `mockPrisma` object (`tests/unit/sales-service.test.ts:36`, `tests/unit/cf-e5-s3-multi-location-stock.test.ts:92`); that pattern is insufficient as a runtime guard because the test object is almost always cast `as unknown as { ... }` to escape strict PrismaClient typing, and the cast strips the typecheck guard. With the alias pattern, both `prisma.$transaction` and `prismaDirect.$transaction` resolve to the same `vi.fn()` at runtime, and no assertion can distinguish "production called the right client" from "production called the wrong client". The stronger guard (CF-E5-S6 round-3 pattern, verified by `tests/unit/job-repo.test.ts`):

     ```ts
     vi.mock("@/lib/db/prisma", () => {
       const prismaTransaction = vi.fn();
       const prismaDirectTransaction = vi.fn();
       return {
         prisma: { /* ... */, $transaction: prismaTransaction },
         prismaDirect: { /* ... */, $transaction: prismaDirectTransaction },
       };
     });
     ```

     Then add a `dual-client wiring (P2028 regression guard)` describe block with one wiring test per `$transaction` helper that asserts `prismaDirect.$transaction` was called and `prisma.$transaction` was not. Any future wrong-client regression fails at unit-test time, not at runtime in production. Mechanical migration cost: update every existing `$transaction` test body to seed `prismaDirectMock.job` and pass `prismaDirectMock` as the `tx` arg.
  5. Concrete self-contained mock template (factories must be self-contained; do NOT reference top-level `const prismaMock` from inside `vi.mock`):
     ```ts
     vi.mock("@/lib/db/prisma", () => ({
       prisma: {
         /* model fields used by the new repo */
       },
       prismaDirect: {
         /* mirror the model fields used inside $transaction callbacks */
       },
     }));
     ```
  6. Run the wiring test in `tests/unit/prisma-dual-client.test.ts` to confirm both clients are distinct and `prismaDirect` is bound to a transaction-safe URL.
  Concrete CF-E5-S6 example: `src/lib/db/job-repo.ts` was added on 2026-06-03 with `import { prisma } from "./prisma";` only, and three of its helpers opened `prisma.$transaction(async (tx) => { ... })`. The unit-test mock aliased only `prisma`; the 472/472 vitest run was a wiring-mock pass, not a production-equivalent pass. The fix is mechanical: import `prismaDirect` from `./prisma`, replace `prisma.$transaction` with `prismaDirect.$transaction` at the three call sites, and update the test mock. The aliasing fix alone (round-2 reviewer recommendation) is insufficient; the round-3 fix uses distinct `vi.fn()` instances for each client's `$transaction` and adds 4 wiring tests. See `references/new-repo-dual-client-regression-review.md` (in `bmad-code-review`) for the full detection checklist including the "stronger guard" pattern and the patch-tool collision pitfall when migrating existing test bodies.
- PITFALL: when addressing review notes (e.g. N1–N3) in a follow-up slice of an existing story:
  - Treat it as a focused bmad-dev-story: same validation gates, same artifact updates.
  - Prefer minimal, localized changes per note (e.g. centralize confirm dialogs, add server-side guard + test, refine E2E locators).
  - Do not turn "notes" into an open-ended refactor; only touch files directly relevant to each note.
- PITFALL (boundary-walk has a second axis — "with related rows" vs "without related rows"): a boundary walk that lists every write path and confirms a derived invariant with related rows present is necessary but not sufficient. Every write path has TWO axes: the related-rows-present axis and the related-rows-absent axis. The second axis is a corner of the input space (legacy cards, brand-new cards with no children, owners with no sales), and corners are where boundary walks most often fail. Concrete symptom from CF-E5-S3 round 3: the second round walked every path for `sum(CardItemLocation.quantity) == CardItem.quantity` and marked all of them green, but two paths (`applyMergeStockForOwner` on a no-bucket card, `adjustBucketQuantitiesForOwner` on a no-bucket card) silently violated the invariant. Build a two-axis write-path table: rows = write paths, columns = invariant hold with related rows present AND invariant hold with related rows absent. If the second column is empty, the table is incomplete. The pattern generalizes to any derived / cross-model invariant (totals, sums, count consistency, role/permission checks).
- PITFALL (test failures with the same error a real production call would produce are usually mock-shape gaps, not production bugs): when a new test for a corrected path fails with an error like "CardItem not found or not owned" or "Cannot read properties of undefined (reading 'create')", check the mock surface before assuming the production code is still wrong. The error message is the same one a real production call would produce under the matching real condition (the card was deleted, the new model field was not added to the mock), so the symptom is confusing. Diagnosis recipe: re-read the production code path the test is exercising, list every prisma / repo method it calls, and compare against the test's `vi.mock` factory. Forgetting to wire `prisma.cardItem.findFirst` (an ownership check inside `$transaction`) is the canonical example; the test fails with a "production-looking" error, the dev agent assumes the production code is wrong, and the actual bug is one missing mock line. Fix the mock, rerun, and the test passes without touching the production code.
- PITFALL (enriching a repo helper to read a previously-unread column breaks prior round's focused tests' mock surface): when a correction round adds an invariant to a repo helper that now reads a column it did not read before (e.g., reading `CardItem.quantity` to enforce `sum(bucket.quantity) == CardItem.quantity` where the prior round only read `{ id, owner_id }`), every prior-round test that mocks the corresponding `prisma.<model>.<findX>` call must be updated to include the new field in its return value. Otherwise the new invariant reads `undefined` and rejects the test setup with the *new* error message ("Bucket total (5) does not match card quantity (undefined)"), which looks like a production-code bug. Run a `grep -n "mockResolvedValue" tests/unit/<prior-slug>.test.ts` after any helper enrichment and patch every return to include the new field. Concrete CF-E5-S4 round-2 example: `tests/unit/cf-e5-s3-multi-location-stock.test.ts` line 184 had to gain `quantity: 5` on the `prisma.cardItem.findFirst` mock because the helper now reads it.
- PITFALL (helper's "no buckets" branch cannot use the delta alone — look up the canonical row's post-mutation quantity): when a helper creates a related row from scratch inside a `$transaction` and the caller's `updateMany` has already mutated the canonical row, the helper's no-buckets branch must read the canonical row's CURRENT quantity, not the signed delta. `Math.max(0, delta)` is wrong for a negative delta on a positive pre-mutation quantity (e.g. card qty 3, sell 1: `Math.max(0, -1) === 0` while post-deduct quantity is `2`). The fix is one extra `tx.canonicalModel.findFirst({ select: { quantity: true } })` inside the helper, gated by `if (bucketQty > 0)` to avoid creating zero-quantity zombies. The pattern generalizes to any "no existing children" branch that needs to size the new child from the canonical row's current state.
- PITFALL (Nth-round bmad-dev-story correction is a real correction — append, do not rewrite): if a fresh `bmad-code-review` returns BLOCKED after a previous correction round, do not rewrite the prior round's Dev Agent Record, do not rewrite the prior round's patterns in the reference file, and do not edit the boundary-walk table in place without adding the new rows. Append a new "round N" section to the story artifact; append a new pattern to the reference file; add new rows to the boundary-walk table (do not delete the corrected rows — the table's history is the story). The reference file grows; the state advances; the artifacts grow. Trying to consolidate prior rounds into a single "the correction" section loses the round-by-round evidence and makes the next reviewer's boundary walk less efficient.

- PITFALL (background-job tick model — concurrency, crash, counter, retry, all four at once): a "many-chunks polled by many clients" background job model (job table + per-chunk tick endpoint + poll-driven progress) is **not** safe by default. The CF-E5-S6 round-2 review caught four co-dependent bugs in one shot; a future round-N correction of the same shape will see the same four. The class-level checklist, in order:
  1. **Atomic claim-and-start.** A plain `getForOwner` + `update({status: 'RUNNING'})` is racy — two overlapping ticks both win, both run the same chunk, and `processed_rows` only advances once (duplicate writes). Use a single `updateMany` with the predicate `WHERE id=? AND owner_id=? AND (status='PENDING' OR (status='RUNNING' AND last_tick_at < cutoff))` and a follow-up `findFirst`; the predicate guarantees only one tick can match. The route returns the current state on `null` (the other tick holds the lease), not 409.
  2. **Advance progress BEFORE the runner's writes.** A crash between the writes and the progress record reprocesses the same chunk (duplicates, regresses stock). The fix is: `claimAndStart` → `advanceProgressBeforeRun` (atomic `$transaction` bumping `processed_rows += chunkSize` iff RUNNING and the new value ≤ `total_rows`) → `runOneChunk` → `recordCountersAfterRun`. The advance-before-write means a crash leaves the next tick starting from the new offset, and the runner's writes are idempotent (see #4). The trade-off: a failed chunk's rows are "consumed with errors" rather than re-attempted. That is honest — `error_rows` carries the failure for the user to re-import manually. Do not be tempted by "advance AFTER writes" (the round-1 design); it is structurally unsafe.
  3. **Counter must reflect actual persistence, not speculative pre-increment.** `result.created += pendingCreates.length` is a lie — it counts rows that might fail inside the helper. Count only what the repo actually returned: `createdCount += created.length` where `created` is the return value of `createMany…ForOwner`. A thrown sub-chunk contributes 0. The `recordCountersAfterRun` helper takes the runner's actual counts, not a synthetic chunk-size delta. Otherwise a failed sub-chunk advances `processed_rows` AND `created_rows`, allowing a job to falsely reach COMPLETED with skipped failed writes.
  4. **Merge writes must be additive, not absolute-set.** `applyMergeStockForOwner({ quantity, buckets })` writes the absolute state; replaying it after a prior partial run overwrites the post-merge DB back to a stale state (regression). The fix is `applyDeltaMergeStockForOwner({ quantityDelta, bucketDelta })` inside one `prismaDirect.$transaction` that reads the current `CardItem.quantity` and `CardItemLocation` rows, ADDS the deltas, asserts `sum(buckets) == CardItem.quantity`, and writes the new state. Replaying adds the same delta again — safe and idempotent. Combined with the runner ALWAYS re-fetching the live existing-cards/existing-buckets snapshot at tick start (one `findMany` per model per tick, ~2-6s on a session pooler — acceptable), the runner sees the post-write state on replay and routes new collisions to the merge path automatically.
  The reference file `references/cardforge-cf-e5-s6-hobby-safe-background-job-csv-import-2026-06-03-round-2.md` (added 2026-06-03) walks through the four findings with concrete code, the call-order test that proves the advance-before-write contract, and the merge-retry test that proves additive idempotency. Apply this checklist to any future story that adds or modifies a per-chunk tick model on a job table; do not assume the round-1 design is safe just because the gates pass.
- PITFALL (same-owner validation must cover EVERY create-path helper): when a repo has multiple create helpers for the same model, the ownership/validation guard must be present in EVERY helper, not just the ones audited during the first implementation pass. A boundary walk that marks "yes, owner-scoped" for a write path is incomplete unless it explicitly confirms the guard is present in the source code. Concrete example from CF-E5-S3 round 4: `createWithInitialBucketForOwner` (manual create path) lacked the same-owner `lotId` guard that `createForOwner` and `createManyWithInitialBucketsForOwner` already had. The fix: add the identical pre-transaction `prisma.lot.findFirst({ where: { id: lotId, owner_id: oid } })` check to every create helper.
- PITFALL (proportional scaling must defend against zero denominator): before any ratio-based distribution of child-row quantities, explicitly guard `if (denominator === 0)`. When all existing child rows have quantity 0, proportional scaling is undefined (`0/0 → NaN`). The fallback depends on domain: for bucket rebalance, collapse to a single bucket at the largest bucket's location with the full new quantity; for cost allocation, skip or throw; for percentages, return 0 or 100. The important thing is deterministic handling, not leaving it to `NaN`. Concrete example from CF-E5-S3 round 4: `updateQuantityForOwner` scaled buckets by `(b.quantity / oldTotal) * newQuantity` and crashed when `oldTotal === 0`. The fix: an `oldTotal === 0` branch that deletes all zero-quantity buckets and creates a single bucket of `newQuantity`.
- PITFALL: writing TS/JS/TSX via execute_code can silently corrupt lines due to tokenization.
- PITFALL (Vitest `mockReset` for queued `mockResolvedValueOnce` pollution): `vi.clearAllMocks()` in `beforeEach` clears mock call history and `.mock.calls`, but it does NOT clear queued `mockResolvedValueOnce` returns. A later test in the same file will inherit the prior test's queued returns (FIFO), so the third test's `listForOwner()` call may receive what the first test's after-create re-fetch expected. Symptom: a test passes in isolation (`vitest -t "..."`) but fails when the full file runs; the failing assertion involves a return shape that the current test never set. Fix in any test that doesn't need chained returns: `mock.mockReset(); mock.mockResolvedValue(expected);` at the top of the test, replacing both `mockReset` (wipes queued returns) and `mockResolvedValue` (sets the single persistent return). Always comment why the reset is needed so the next agent doesn't simplify it back to `clearAllMocks` and reintroduce the bug.
- PITFALL (Vitest + Next.js unit tests):
    - Calling Next.js server actions in unit tests can fail due to:
      - revalidatePath expecting a static generation store.
      - vi.mock hoisting issues where top-level variables are referenced before initialization.
    - Fix:
      - Mock next/cache: vi.mock("next/cache", () => ({ revalidatePath: vi.fn() })).
      - **Keep vi.mock factories self-contained — define the mock object inline inside the factory, not by referencing a top-level const.** Vitest hoists `vi.mock` calls to the top of the file before imports run, so any top-level reference is `undefined` at hoist time and throws `ReferenceError: Cannot access 'xxx' before initialization`.
        - Wrong (top-level const referenced inside the factory):
          ```ts
          const prismaMock = { job: { findFirst: vi.fn() } };
          vi.mock("@/lib/db/prisma", () => ({ prisma: prismaMock })); // ReferenceError at hoist time
          ```
        - Right (factory is self-contained, no top-level reference):
          ```ts
          vi.mock("@/lib/db/prisma", () => ({
            prisma: { job: { findFirst: vi.fn() } },
          }));
          import { prisma } from "@/lib/db/prisma";
          const prismaMock = prisma as unknown as { job: { findFirst: ReturnType<typeof vi.fn> } };
          ```
      - Use mock functions inside the factory, not from the outer scope.
    - Symptom: typecheck fails on a line that "looks fine" in the summary but has garbled syntax when read back, OR the test fails with `ReferenceError: Cannot access 'prismaMock' before initialization` at the top of the failed file. Fix: move the mock object into the factory's return literal. Concrete CF-E5-S6 example: `tests/unit/job-repo.test.ts` originally had `const prismaMock = { ... }; vi.mock("@/lib/db/prisma", () => ({ prisma: prismaMock }));` which threw at hoist time; the fix was inlining the mock object inside the factory and accessing it via `prisma as unknown as { ... }` after the import.

- PITFALL (Vitest + Next.js route handlers):
    - Directly invoking Next.js route handlers (e.g., GET from app/api/...) with plain `Request` objects in Vitest is fragile:
      - They expect `NextRequest` (cookies, nextUrl, etc.).
      - In jsdom, `new Request()` lacks the internal symbols Next.js uses for cookie parsing, so `new NextRequest(new Request(...))` returns `undefined` for `cookies.get(...)`.
      - Auth middleware and Supabase SSR helpers often fail or return 401/500 in unit context.
      - Result: flaky or misleading “route tests” that test wiring noise, not your logic.
    - Preferred pattern for behavior-level route tests:
      - Mock `requireAuthedOwnerId`, `getShopifyConfig`, and service-layer functions (`buildOAuthStart`, `handleOAuthCallback`).
      - Construct a lightweight mock `NextRequest` as a plain object with the surface the route actually touches:
        ```ts
        function makeNextRequest(url: string, cookieMap: Record<string, string> = {}): unknown {
          const parsed = new URL(url);
          const cookies = new Map<string, { name: string; value: string }>();
          for (const [name, value] of Object.entries(cookieMap)) {
            cookies.set(name, { name, value });
          }
          return {
            url,
            nextUrl: parsed,
            cookies: {
              get(name: string) { return cookies.get(name); },
            },
          };
        }
        ```
      - Pass this mock directly to the route handler (`startGET(mockReq as any)` or `startGET(mockReq as unknown as NextRequest)`).
      - Assert on `res.status`, `res.headers.get("location")`, and `res.headers.get("set-cookie")` for redirect/cookie behavior.
      - Assert that mocked service functions were called with expected params.
    - Fallback pattern when full behavior tests are too noisy:
      - Test business logic in service/repo layers with mocks.
      - For routes, do static checks only (export exists, imports correct).

- PITFALL (NextResponse.redirect requires absolute URLs):
    - `NextResponse.redirect("/shopify?error=foo")` throws at runtime because Next.js validates the URL as absolute.
    - In route handlers, always construct absolute redirect URLs (e.g., `\${appUrl}/shopify?error=...`) or return JSON error responses for missing-config cases.
    - If `appUrl` may be undefined in a missing-config branch, return `NextResponse.json({ error: "..." }, { status: 503 })` instead of a redirect.

- PITFALL (Crypto/OAuth key validation tests):
    - When testing encryption key validation (e.g., SHOPIFY_TOKEN_ENCRYPTION_KEY), ensure test inputs actually match the condition:
      - A “all letters” test must use only letters.
      - A “too short” test must be shorter than the enforced minimum.
    - If the test key accidentally satisfies other rules (e.g., includes digits), it becomes a false positive.
    - Always align the test value with the exact validation rule it is meant to fail.
  - Mitigation:
    - For tricky files (E2E specs, complex components), prefer:
      - read_file + patch for small, targeted edits.
      - Or write_file via execute_code with a Python script that constructs content programmatically (no raw pasted JS in the prompt).
    - After writing, always:
      - read_file the affected lines.
      - Run typecheck/lint immediately.
    - If a file repeatedly breaks at the same line, stop rewriting the whole file; use patch or sed to fix that line only.

## Local web app runtime smoke (browser vs Playwright)

- Pitfall: the browser tool (browser_navigate) often cannot reach local dev servers on 127.0.0.1 due to sandboxing (ERR_CONNECTION_REFUSED), even when curl works.
- When runtime smoke or browser QA is required for a local Next.js/Node app:
  - Prefer:
    - Playwright E2E tests run via terminal (npx playwright test) as the primary “smoke” mechanism.
    - Or expose via a tunnel (e.g., ngrok) and use browser_navigate on the public URL.
  - Do not:
    - Assume browser_navigate to http://127.0.0.1:3000 will work.
    - Loop-retry the same failing browser_navigate call.
  - If the user asks “can you smoke this in the browser?”:
    - Explain briefly that the browser runtime is sandboxed.
    - Offer: (1) Playwright E2E smoke, (2) tunnel-based browser smoke, or (3) a guided checklist for the user.

## Workflow State Transitions

```json
{
  "workflow_status": "implemented_not_reviewed",
  "active_workflow": "bmad-code-review",
  "last_story_id": "<story-id>",
  "next_recommended_workflows": ["bmad-code-review for <story-id>"]
}
```

## Pre-Existing Test Failures

If `pnpm test` fails on a pre-existing unrelated test (different story, same file), note it and continue. Do not fix out-of-scope failures. Document: "pre-existing failure in `<file>:<line>` — `<test name>`, unrelated to this story."

## Reusable patterns (any project)

These are not project-specific. Apply them in any `bmad-dev-story` that touches a similar shape.

### Narrower repo helper when the client must NOT supply a calculated value

When a story requires a server-side authoritative calculation (cost-basis, per-unit allocation, derived status) and explicitly forbids the client from submitting the computed field, do not extend an existing `bulkUpdateForOwner` boundary with a new optional `costBasisPence` field. Add a narrower repo helper such as `assignLotForOwner(ownerId, ids, lotId)` that verifies ownership, computes the derived value internally, and calls `updateMany` with the computed value. The narrower boundary encodes the "client cannot influence the calculation" rule at the type system level. Add at least one test that sends a malicious `costBasisPence` in the form and asserts the repo is called with the server-computed value.

### Deliberate string sentinel for null filter values

For "filter to rows where column IS NULL" (or any nullable filter), never overload numeric 0, empty string, or any "natural" empty value. Use a deliberate string sentinel (`__none`) exposed as a named constant, accepted via a Zod `z.union([z.literal(SENTINEL), z.coerce.number().int().positive()])`, and reject 0 explicitly in the schema. Map the sentinel to a Prisma where clause via a discriminated union. See `references/cardforge-cf-e5-s2-bulk-lot-assignment-2026-06-02.md` for the CF-E5-S2 implementation.

### Page passes raw URL string to schema; do not pre-coerce with `Number()`

When a Next.js page parses `searchParams` and forwards to a Zod schema that needs to discriminate between a numeric value and a string sentinel, do not pre-coerce with `Number()` — it destroys the sentinel (`Number("__none")` is `NaN`). Pass the raw string; let `z.union` + `z.literal` match the sentinel first.

### Two visible controls > one ambiguous control

When the user can do two semantically opposite things to the same field (assign vs clear), use two distinct server actions, not one overloaded action with a flag. The UI keeps the two controls visibly separate, validation rules diverge cleanly, and tests can assert each action's boundary independently.

### Back-compat shim for refactors with a legacy test surface

When a story splits a monolithic export (e.g. `importCsvToLotAction(formData)`) into a new async shape (e.g. `submitCsvImportAction(input) + runOneChunk(job)`) and existing tests import the legacy export directly, do NOT delete the legacy export. The tests are part of the contract. Refactor the legacy export into a thin shim that delegates to a shared internal function (e.g. `runImportCore`) and have both the legacy shim and the new async path call that shared function. This:

- Preserves the legacy test surface end-to-end (CF-E5-S5's `csv-import-large-batch.test.ts` still passes 6/6 after the CF-E5-S6 split).
- Ensures both code paths exercise the same write logic so chaos-sort semantics, the no-bucket seed correction, and `prismaDirect` `$transaction` writers cannot drift between the two paths.
- Adds one well-named internal function and a 3-line shim, not a fork.

Do NOT take a "while I'm here" shortcut to delete the legacy export and rewrite the test — that's scope creep into a test-surfaced refactor, and the BMad operating model forbids it. The carry-forward concerns in `sprint-status.yaml` are the documented home for "this refactor split is a risk surface" until the next code-review closes the loop.

## Supabase Auth, Middleware, Migration, and RLS (Finish-Gate Pattern)

When a story requires wiring Supabase auth, route protection, migrations, and RLS checks (e.g., MVP finish-gate), follow this concise pattern instead of free-form design:

- RLS migration: use raw SQL via Prisma migration to:
  - ALTER TABLE ... ENABLE ROW LEVEL SECURITY.
  - CREATE POLICY per table using auth.uid() joined via user_profiles.auth_uid → owner_id.
- Auth guard: centralize auth validation in server actions:
  - Use a helper (e.g., requireAuthedOwnerId()) that wraps resolveCurrentOwnerId()
    and throws a clear AuthError when auth is missing/invalid.
- Middleware:
  - Protect dashboard routes; redirect unauthenticated to /login.
  - Redirect authenticated from /login to /dashboard.

See: references/cardforge-rls-and-auth-hardening-pattern-2026-05-28.md for a concrete example used in CF-E2-S3.

> See: `references/cardforge-rls-and-auth-hardening-pattern-2026-05-28.md` for a concrete RLS + auth-guard pattern used in CardForge CF-E2-S3.

- Auth layer:
  - Use `@supabase/ssr`:
    - `createBrowserClient` in a client helper (e.g., `src/lib/auth/client.ts`).
    - `createServerClient` in a server helper (e.g., `src/lib/auth/server.ts`) using `cookies()`.
  - Keep all Supabase access behind these helpers; do not inline env reads in pages.
  - PITFALL (CF-E1-S7): Supabase SSR requires cookie setters for auth-changing calls (signOut, updateUser, etc.).
    - If your server client only implements `get(name)`, operations like signOut() may:
      - Appear to succeed,
      - Redirect,
      - But leave auth cookies intact → user is still “logged in” until they manually clear cookies.
    - Required: implement `setAll` (preferred) or `set`/`remove` (deprecated but still used) in the `cookies` config of `createServerClient`.
    - If you see “auth/session issues” or silent sign-out failures, this is almost always the cause.

- Login / logout:
  - Implement email/password sign-in and sign-up in a `/login` page.
  - Provide a simple sign-out route (e.g., `POST /api/auth/signout`) that:
    - Calls `supabase.auth.signOut()`.
    - Redirects to `/login`.
  - Show clear error messages for auth failures (wrong password, not confirmed, etc.).

- Route protection (middleware):
  - Use Next.js middleware (e.g., `src/middleware.ts`) to:
    - Redirect unauthenticated requests under protected prefixes (e.g., `/dashboard`) to `/login`.
    - Redirect authenticated users from `/login` to `/dashboard`.
  - Matcher should exclude static assets and internal paths.
  - PITFALL: do not import middleware directly in unit tests as a normal module; it is runtime-specialized. Instead, validate its existence and behavior indirectly (file presence, route behavior, or integration tests).

- UserProfile / owner resolution:
  - On first access (e.g., via `/dashboard` or a dedicated `/api/auth/ensure-profile`), upsert a `UserProfile` row by `auth_uid`.
  - Ensure `resolveCurrentOwnerId()` or equivalent:
    - Uses Supabase session → `UserProfile` → owner id in production.
    - Uses an explicit, dev-only fallback (e.g., `OWNER_ID`) that is disabled in production unless explicitly allowed.
  - PITFALL: never silently default to owner 1 in production.
  - PITFALL (CF-E1-S7): do NOT implement UserProfile bootstrap as a self-fetch from a layout or page.
    - A fetch to an app-local route (e.g., /api/auth/ensure-profile) from a server component:
      - Often does not forward the same request cookies.
      - Often silently swallows non-OK responses.
      - Leads to “logged in but no UserProfile” failures in owner-scoped queries.
    - Preferred pattern:
      - Create a server-only helper (e.g., src/lib/auth/ensure-profile.ts):
        - export async function ensureCurrentUserProfile(authUid: string): Promise<number>
        - Uses Prisma directly (no HTTP) to upsert UserProfile.
        - Returns profile.id as owner_id.
      - Call this helper from the layout or route after getUser(); if it fails, block or redirect instead of continuing.

- Migrations and RLS:
  - Confirm migrations:
    - Use `prisma migrate status` to inspect.
    - Use `prisma migrate deploy` for production/remote databases (non-interactive).
  - Check RLS:
    - Query `pg_tables` for `rowsecurity` on business tables.
    - If RLS is disabled and the app relies on app-level owner_id filtering:
      - Record this as an explicit MVP risk in the story and CONTINUE-HERE.
      - Do not silently assume “RLS is on” or “Postgres enforces it for us.”
  - PITFALL: Supabase enables RLS by default for new tables, but Prisma-created tables or custom migrations may leave it disabled. Always verify.

- Evidence:
  - In the Dev Agent Record, explicitly separate:
    - Static validation (lint, typecheck, tests, build, prisma validate, git diff --check).
    - Migration status (applied/verified or blocked and why).
    - RLS status (enabled/disabled and rationale).
    - Browser/runtime smoke (done or deferred with exact human action required).

- PITFALL (CF-E1-S7): never use NEXT_PUBLIC_SUPABASE_URL as the base for app-local API routes.
  - Symptom: code constructs URLs like:
    - `${NEXT_PUBLIC_SUPABASE_URL}/api/auth/ensure-profile`
    - `${NEXT_PUBLIC_SUPABASE_URL}/api/auth/signout`
  - NEXT_PUBLIC_SUPABASE_URL is the Supabase project host (e.g., https://<project>.supabase.co), not the Next.js app origin. Requests to it will:
    - Not reach your app’s route handlers.
    - Not forward the app’s auth cookies.
  - Correct patterns:
    - For server components/layouts calling app routes:
      - Derive origin from request headers:
        - const proto = headerStore.get("x-forwarded-proto") ?? "http";
        - const host = headerStore.get("x-forwarded-host") ?? headerStore.get("host");
        - const base = `${proto}://${host}`;
      - Use base + "/api/auth/ensure-profile" etc.
    - For sign-out:
      - Prefer a server action that calls Supabase signOut() and redirect() directly, or POST to the local /api/auth/signout route.
    - For client components:
      - Use relative URLs (e.g., "/api/auth/ensure-profile") instead of NEXT_PUBLIC_SUPABASE_URL.

- PITFALL (CF-E1-S7): Next.js auto-generated types reject extra exports from layout modules.
  - If you export a server action directly from a layout module (e.g., src/app/(dashboard)/layout.tsx), Next.js may fail typecheck with:
    - "Property 'signOutAction' is incompatible with index signature."
  - Fix:
    - Move the server action into a dedicated file (e.g., src/lib/auth/signout-action.ts) and import it into the layout.
    - Keep the layout module exports limited to Next.js-recognized symbols (default, metadata, etc.).

See: `references/cardforge-cf-e1-s7-auth-middleware-and-rls-pattern-2026-05-25.md` for a concrete example.

## Output Requirements

For each story, produce:
- All source files (actions, components, pages, schemas)
- Schema unit tests (10+ covering valid/invalid/edge cases)
- Artifact updates (state.json, sprint-status.yaml, CONTINUE-HERE.md, story Dev Agent Record)
- Validation evidence (gate results, file list)

## Artifact Format

Append to the story artifact:

```markdown
## Dev Agent Record

**Completed**: YYYY-MM-DD
**Files changed**: <list>
**Validation**: <gate results>
**Key decisions**: <list>
**Notes**: <any unresolved or deferred items>
**Next**: bmad-code-review for <story-id>
```