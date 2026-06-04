# Next.js / Prisma expenses ledger review pattern — CardForge CF-E1-S5

Use this reference when reviewing an expenses ledger or similar money-entry CRUD story where the product asks for user-facing currency while storing integer minor units.

## Concrete blocker pattern

A story can appear to satisfy “integer pence internally” while still failing “GBP user-facing” if the form exposes the storage unit directly.

Block when:
- Create/edit forms label the input as `Amount (pence)` or otherwise ask users to enter pence.
- Edit forms pre-fill the raw persisted pence value into a visible currency input.
- Server actions read a submitted field such as `amountPence` and persist it directly, with no GBP-to-pence conversion boundary.
- Tests only prove schema validation of `amountPence`, not the user-facing currency conversion behavior.

Passing shape:
- User-facing form accepts GBP-style values, e.g. `5`, `5.00`, or a clearly labelled pounds field.
- A deterministic boundary converts GBP decimal input to integer pence before repository writes.
- Edit forms display persisted pence as GBP decimal text, not raw pence.
- Validation rejects blank, non-numeric, negative, zero, and over-precision values according to the story semantics.
- Focused tests cover conversion, create/update action payloads, and edit prefill behavior where practical.

## Test evidence expectations

When the story explicitly asks for focused tests covering validation, owner-scoped action behavior, currency conversion, and archive/delete behavior, a schema-only test file is not enough.

Look for focused coverage of:
- create action resolves owner and writes converted pence;
- update action resolves owner and writes converted pence/null-cleared optional fields;
- archive/delete actions call owner-scoped repository methods;
- invalid currency input does not write;
- archived expenses are hidden from the active ledger.

Existing repository owner-scope tests can count for repository coverage, but not for server-action conversion or archive/delete action behavior unless they exercise those production boundaries.

## Optional-field clearing edit-path blocker

When a story says users can edit all captured expense fields, optional text fields such as vendor/source and notes/reference must be clearable, not just changeable to another non-empty value.

Block when:
- Server actions build raw update payloads with `formData.get("vendor")?.toString() || undefined` or equivalent before validation.
- A later `"" -> null` branch exists but is unreachable because blank strings have already been collapsed to `undefined`.
- Repository updates receive `vendor: undefined` / `notes: undefined`, causing Prisma to leave old values unchanged instead of clearing the fields.
- A focused action test name claims blank fields become null but the assertion expects `undefined`, thereby encoding the regression as passing evidence.

Passing shape:
- Preserve blank-string intent through parsing for fields that the UI renders as clearable.
- Convert blank optional edit fields to `null` at the action/schema boundary before repository writes.
- Focused tests assert blank edit submissions call the owner-scoped repository with `vendor: null` and `notes: null` (or the project’s explicit canonical clear sentinel).
- Partial update paths that omit the field entirely can still use `undefined` to mean “leave unchanged”; distinguish omission from an intentional blank submission.

## Archived-row visibility note

If an expenses page fetches all owner expenses and filters archived rows in a client component, the visible ledger can still be correct but archived rows are unnecessarily sent to the browser. Treat as a non-blocking note unless the story or security model explicitly requires server-side active-only filtering. Prefer a repository/page query boundary such as `where: { owner_id, archived: false }` or a dedicated active-list helper.

## Post-correction passing review pattern

After the GBP-entry and optional-field blockers are corrected, a passing expenses review should explicitly re-check:
- create/edit forms expose `amountGbp` / `Amount (GBP)` and edit prefill converts persisted pence with `(amount_pence / 100).toFixed(2)` or an equivalent display helper;
- create/update actions convert GBP to pence before Zod/repository writes and focused tests assert representative conversions such as `5.00 -> 500` and `12.34 -> 1234`;
- edit action preserves blank `vendor` / `notes` FormData strings long enough to map them to `null`, while create action still avoids persisting unwanted empty strings;
- focused action tests exercise production action boundaries for create/update/archive/delete, owner id propagation, GBP conversion, blank edit null-clearing, non-blank edit persistence, and invalid amount no-write behavior;
- active ledger rows are filtered at the repository/page query boundary (`archived: false`) before rows reach the client, not only hidden by client-side filtering.

Use `PASS WITH NOTES` when these source/test checks pass but runtime browser smoke and live Supabase/RLS remain unverified. Reconcile the story/status/state/continuation docs to the fresh review verdict, and route next workflow to state-check for the next story rather than leaving stale correction/re-review wording.

## Artifact handling note

If a review is performed while the implementation diff itself is still uncommitted, append/reconcile BMad review artifacts as usual, but do not create a standalone review commit unless the repo workflow explicitly wants mixed uncommitted implementation + review state committed together. Report the verdict and leave the correction workflow to commit a coherent implementation/correction set.
