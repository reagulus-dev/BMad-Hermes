---
name: bmad-code-review
description: Perform a structured BMad code review as a progression gate using repo truth, validation evidence, and explicit pass/fail reasoning.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, code-review, validation, quality, gatekeeping]
    related_skills: [bmad-dev-story, bmad-evidence-reporting, bmad-state-check]
---

# BMad Code Review

## Model Routing for BMad Code Review

When delegating BMad code review via `delegate_task`, use a higher-accuracy model:

| Review type | Recommended model | Provider |
|-------------|-------------------|----------|
| Gate code review | `gpt-5.5` | `openai-codex` |
| Quick ad-hoc review | Current default | — |
| Large diff review | `gpt-5.5` or `claude-sonnet-4` | `openai-codex` or `anthropic` |

Rationale: Code review benefits from deeper code comprehension and edge-case spotting. The local llama.cpp model works for implementation stories where the prompt contains full task context, but code reviews often need broader analysis that benefits from a larger model.

**Pre-delegation check (don't waste a 600s timeout).** Before kicking off a code-review subagent, inspect `~/.hermes/config.yaml` for an actual `codex` provider. A common failure mode is delegating with the skill's recommended provider/model but the config has no codex entry (only the default model, or only `openai-codex` commented out). The subagent then either falls back to the default model (silently producing a low-accuracy review that is NOT a valid code-review gate per the model-authorization rule below) or times out at 600s with no review produced. If `~/.hermes/config.yaml` has no `codex` provider entry, do not delegate — run the review locally in the orchestrator turn using this skill, OR ask the founder whether to enable a codex provider, OR proceed with the default-model review and explicitly record the model in the review verdict so the verdict is honest about its accuracy tier.

Model-authorization rule:
- If the user or project workflow has pinned BMad code review to a higher-accuracy model, do not treat a review produced by a cheaper/unauthorized model (for example MiniMax M2.7 when it was intended only for another agent role) as valid evidence.
- A low-cost model review can be read only as stale context/risk hints; its verdict and notes are not a progression gate.
- Run a fresh authorized review, record the invalid model/review commit explicitly, and reconcile status/evidence anchors to the fresh review.

Configuration tip: Set `delegation.model: gpt-5.5`, `delegation.provider: openai-codex`, `delegation.base_url: https://chatgpt.com/backend-api/codex` in config.yaml before delegating code review tasks. Switch back to llama.cpp for dev-story after review to keep costs low.

If the delegated review times out (for example, 600s):
- Do not assume failure; partial work may have completed.
- Immediately inspect the repo:
  - `git log --oneline -5` to see if a review commit was created.
  - `git status --short` to see staged/modified BMad artifacts.
  - Open the story artifact and check whether review findings were appended.
  - Open `_bmad/state.json` and `_bmad/sprint-status.yaml` for any changes.
- If partial work was persisted:
  - Treat as incomplete.
  - Decide:
    - If the partial review is coherent and only missing a subset of ACs or evidence, continue the review in the same turn using this skill, or
    - Run a focused re-review on the areas missing assessment.
  - Do NOT blindly re-delegate.
- If nothing was persisted (no new commit, no artifact changes):
  - Run the review yourself in this turn using this skill.
  - Use the same review inputs: story artifact, changed files, tests, `_bmad/state.json`.
  - Do not silently re-delegate; treat the timeout as “delegate failed, fall back to local review.”
- Never let a timeout silently stall the workflow or force the user to chase a hung subagent.

## When to Use

Use after a meaningful implementation change, bug fix, or story completion attempt.

## Goal

Prevent false completion by making review a real progression gate instead of a formality.

## Canonical Naming Rule

For BMad-managed live state, use `snake_case` consistently.

Preferred field names include:
- `workflow_status`
- `last_review_summary`
- `last_evidence_path`
- `last_artifacts`
- `next_recommended_workflows`
- `updated_at`

Do not continue schema drift by introducing new review-state references in camelCase.

## Review Inputs

Inspect as many of these as are available:
- the target story or fix description
- the canonical story artifact for that work when available
- changed files and diff context
- relevant tests and validation results
- `_bmad/state.json`
- evidence artifacts under `_bmad/artifacts/evidence/`
- prior review, QA, or handoff artifacts
- runtime verification notes when the change affects real user flows

## Review Dimensions

Check for:
- correctness relative to the requested change
- obvious regressions or edge cases
- missing validation
- maintainability or clarity problems that materially affect trust
- mismatch between claim and evidence
- stale or inaccurate workflow state
- missing acknowledgment of unverified runtime areas

### Mobile Visual Polish / Premium Shell Reviews

When a story is primarily visual polish, premium shell, or design-system rollout, also check:
- whether the scope stayed bounded to the named screens/components rather than becoming an unreviewable redesign
- whether shared tokens/components compile across native and web targets after the style changes
- whether React Navigation chrome has accidental defaults such as placeholder tab icons/glyphs, unexpected labels, or broken safe-area/tab spacing
- whether Android screenshot/XML evidence proves the exact screens claimed, using unique root `testID`s or screen-specific hero copy rather than screenshot filenames alone
- whether a screenshot captured auth, launcher, recents, or the wrong tab while the summary still says `PASS`
- whether the verdict distinguishes source/build/export coverage from true screen-level runtime visual evidence
- whether human visual approval, iOS runtime, and founder-review readiness remain explicitly unclaimed unless separately verified

Use `PASS WITH NOTES` when the implementation is sound but visual-runtime evidence is partial. Use `BLOCKED` when the evidence summary mislabels the wrong screen as a verified screen or obvious shell regressions ship in screenshots/XML.

### Supabase / Postgres Foundation Reviews

When a story introduces Supabase schema, RLS, tenant membership, or onboarding/setup writes, also check:
- recursive RLS policy paths, especially policies on membership tables querying parent tables while parent-table policies query membership tables
- parent + membership creation split across multiple client calls instead of one transactional RPC/database function
- parent + child-row edits split across multiple client calls when one user action requires atomicity (for example booking fields plus quote rows)
- direct insert policies that bypass required setup invariants
- cross-tenant integrity gaps where independent foreign keys do not prove referenced rows belong to the same tenant/establishment/household
- additive marketplace/Shopify foundation tables whose child rows have their own `owner_id` but plain integer FKs to another owner-scoped table. For owner-scoped connection/listing/allocation/webhook tables, verify composite owner-consistent FKs such as `(connection_id, owner_id) -> shopify_connections(id, owner_id)`, `(listing_id, owner_id) -> shopify_listings(id, owner_id)`, and `(card_item_id, owner_id) -> card_items(id, owner_id)`. RLS that checks only the child row's `owner_id` is not enough if the DB relation permits cross-owner references. See `references/cardforge-shopify-owner-consistency-review.md`.
- owner-scoped Prisma/repository helpers that accept related row IDs (`lotId`, `cardItemId`, `projectId`, etc.) without checking the referenced row belongs to the same owner/tenant before create/update
- production pages, route handlers, or server actions that pass a hardcoded/dev owner ID (for example `ownerId = 1` or `getDevOwnerId()`) into otherwise owner-scoped repositories while the story claims authenticated owner-scoped flows; repository filters are not sufficient if every request is silently mapped to the same owner. Treat this as BLOCKED unless the route/action is explicitly gated as unavailable/dev-only or the story formally scopes out live owner-authenticated access.
- corrections that replace `ownerId = 1` with an environment-only helper but still leave production-facing routes/actions on a development seam. Prefer a centralized server-only resolver that checks Supabase/session user first, resolves through the user profile table, allows `OWNER_ID` only as an explicit local-dev fallback, and disables that fallback in production unless deliberately overridden. Use PASS WITH NOTES when this safe seam exists but full auth UX/live RLS smoke remains future scope; see `references/prisma-owner-resolver-correction-review.md`.
- Next.js/Supabase auth stories that use `NEXT_PUBLIC_SUPABASE_URL` as the base for app-local `/api/...` route calls from layouts/server actions. That env var is the Supabase project host, not the application origin; profile bootstrap and sign-out can silently target `https://<project>.supabase.co/api/...` instead of the app. Treat as BLOCKED when first-user profile creation/resolution or sign-out is in scope. Prefer direct server-only helper calls, local route form posts, framework server actions, or an explicit app-origin env var. Also verify cookie/session semantics, not just URL shape: a server component/layout self-fetch to an app-local auth route must forward authenticated cookies or be replaced by a direct helper; non-OK profile bootstrap must not be swallowed if downstream owner-scoped pages require the profile; Supabase SSR sign-out boundaries must expose cookie setters (`setAll` preferred, deprecated `set`/`remove` acceptable when correct) so redirects actually clear auth cookies. Source-regex tests can guard a past wrong-host bug but do not by themselves prove profile/sign-out behavior. See `references/nextjs-supabase-auth-route-origin-review.md`.
- whether validation claims distinguish TypeScript/build checks from live Supabase migration, lint, and RLS smoke verification
- whether service/UI validation is being mistaken for DB-level hardening; if a domain invariant is only enforced in app service code, request/record a direct-write smoke boundary and use `PASS WITH NOTES` unless the story explicitly requires database enforcement
- for additive marketplace/channel tables with `owner_id` plus references to connections/listings/inventory rows, whether child rows can point at another owner's parent/resource by guessed integer ID. Prefer composite `(id, owner_id)` unique keys plus composite FKs such as `(connection_id, owner_id) -> (id, owner_id)` and focused schema/migration tests. Block owner-scoped persistence stories when only the child row's `owner_id` is checked. See `references/marketplace-owner-consistency-review-cardforge-cf-e4.md`.
- whether persistence modules expose a clear canonical public interface (for example `DbProfileStore`) and mark other helpers as internal/test-only; if helpers are exported, they should be documented as not intended for external callers

For Shopify OAuth connection stories, additionally verify token encryption key shape/length validation, owner-scoped connection repository/service tests, no-secret client status payload tests, route/callback tests for nonce/state/HMAC/error paths, and that mocked OAuth tests are not overclaimed as live dev-store verification. Block when required focused owner/route tests are absent even if the full build/test bundle passes. See `references/cardforge-shopify-oauth-connection-review.md`.

See `references/supabase-rls-foundation-review.md` for a concise checklist and examples.
See `references/prisma-owner-scoped-relation-review.md` for the concrete Prisma owner-scoped relation and production-helper test pattern.
See `references/production-module-owner-scope-test-review.md` for the specific pitfall where behavioral tests still use a test-only injectable repository clone instead of the production module.
See `references/production-module-owner-scope-test-pattern.md` for the concrete Vitest+TypeScript pattern: dynamic import for mock access, minimal prisma mock shape, and the exact test structure that exercises production repo helpers.
See `references/supabase-service-validation-vs-db-hardening.md` for handling service-path validation that protects current app flows while DB triggers/RPC hardening remains deferred.

### New-Repo Dual-Client Regression (class-level pitfall, applies to any project with a pooler/direct split)

**NEW: this is a class-level pitfall, not just a Next.js / Prisma CRUD pitfall.** When a story adds a new repo module (e.g. `jobRepo`, `bulkImportRepo`, `webhookRepo`) on top of an already-deployed dual Prisma client (pooler for reads + direct/session-pooler for `$transaction` writers), the rule "every `prisma.$transaction(async (tx) => { ... })` site routes to `prismaDirect.$transaction(...)`" is global, not scoped to the original repo (`owner-scope.ts` in CardForge CF-E5-S5). The wrong-client usage is silent: the unit-test mock for the new repo only aliases `prisma`, so `prisma.$transaction` and `prismaDirect.$transaction` resolve to the same `vi.fn()` and the 100% passing test run does not catch the regression. The first live production tick will hit P2028 on the second statement inside the `BEGIN`/`COMMIT` envelope.

Three-line detection checklist (use on every new repo that uses `$transaction`):
1. **The new repo uses `prismaDirect.$transaction(...)`, not `prisma.$transaction(...)`.** Grep the new file.
2. **The unit-test mock exposes distinct `prisma` and `prismaDirect` mock surfaces** (preferred) with separate `vi.fn()`-backed `$transaction` instances. The minimum acceptable pattern is `prismaDirect: mockPrisma` alongside `prisma: mockPrisma`; the stronger guard is two distinct `vi.fn()` instances plus a `dual-client wiring (P2028 regression guard)` describe block with one test per `$transaction` helper asserting `prismaDirect.$transaction` was called and `prisma.$transaction` was not.
3. **The Dev Agent Record's contract matches the implementation.** If the carry-forward says "no `$transaction` writers in the new repo" and the implementation has them, the contract is wrong or the code is. Either re-route to `prismaDirect` or amend the contract with a rationale.

See `references/new-repo-dual-client-regression-review.md` for the full concrete CardForge CF-E5-S6 round-2/round-3 pattern, including the verdict-shaping language template and the patch-tool collision pitfall when migrating `prismaMock` → `prismaDirectMock` via `replace_all=true`. See also `references/prisma-supabase-transaction-pooler-p2028.md` for the original symptom/root-cause/fix reference.

### Next.js / Prisma CRUD Reviews

When a story introduces Next.js pages, server actions, Zod validation, and Prisma owner-scoped CRUD/list/detail flows, also check:
- DB-backed pages are not accidentally statically prerendered by `next build`; dynamic output for routes like list/detail/inventory pages is meaningful evidence when the story says build should not prerender DB data.
- create/update/filter schemas reject client-controlled owner/identity fields and validate optional filter combinations without broadening access.
- server actions use `safeParse` or an equivalent validation boundary before repository calls and revalidate every affected list/detail path after successful mutations.
- Prisma repository helpers constrain by owner at the query boundary, not after fetching a broader set.
- create/update operations that attach a related row, such as creating a card item for a lot, prove that related row belongs to the same owner before writing.
- list filters compose into a single owner-scoped query where practical, and focused tests cover representative combinations rather than only the no-filter happy path.
- summary fields such as counts, allocated cost, sold revenue, and profit have inspected formula semantics and focused tests, including archive/delete inclusion rules and null/decimal behavior.
- money-entry stories distinguish user-facing currency from persisted minor units: if an AC says "GBP user-facing and integer pence internally," block forms that expose raw pence entry (`Amount (pence)`, `amountPence` fields prefilled with stored pence) instead of converting a GBP decimal input at the action/schema boundary.
- edit flows for optional captured fields must distinguish omission from intentional clearing: if the UI renders editable vendor/source or notes/reference fields, blank submissions must be able to clear existing values (typically by preserving `""` through parsing and writing `null`). Block actions that collapse blanks to `undefined` before validation, because Prisma-style updates then leave old values unchanged. Focused action tests should assert `null` clearing rather than encoding `undefined` as the expected result.
- focused test evidence matches the story contract: schema-only tests do not satisfy ACs that explicitly require action behavior, currency conversion, archive/delete behavior, or owner-scoped server-action coverage.
- lint evidence distinguishes pre-existing unrelated warnings from warnings introduced by the reviewed slice; if the project gates on zero warnings, a new warning is an evidence mismatch.

For expenses-ledger reviews with GBP entry and pence storage, see `references/nextjs-prisma-expenses-gbp-review-cardforge-cf-e1-s5.md` for the concrete CardForge CF-E1-S5 blocker and correction pattern.
- For async/client-polled background job stories that move CSV imports or other batch work off a synchronous Server Action/request runtime, also check server-side claim/progress/idempotency safety, not just happy-path polling UI and passing validation. Block when a tick route uses a plain mark-running update after a separate fetch, writes domain rows before progress is safely recorded, counts attempted writes as processed, or uses stale submit-time snapshots for retryable merge semantics. See `references/client-polled-background-job-review.md`.