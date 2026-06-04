# Pure grouping policy review pattern (HLX-5.5)

Use this when reviewing pure orchestrator grouping/cart policy helpers that do not yet launch browser workers or persist DB state.

## Blocker patterns observed

1. Typed ownership boundary is missing
- If the AC says grouping must not cross worker/profile/cart/session/vendor boundaries, the candidate/grouping input contract must carry enough typed ownership fields to enforce that boundary.
- Do not accept comments like “selection happened before this policy call” as enforcement when the story requires the policy/boundary itself to reject mismatches.
- Do not accept `(candidate as any).profile_id` or correlation-id parsing as the only profile/cart boundary model. Correlation parsing can be a compatibility helper, not the typed contract.
- Required tests should include cross-worker, cross-profile, cross-cart/session, cross-vendor, and an all-valid same-owner grouping case.

2. Known-worker enforcement is optional
- If a carry-forward or AC says the concrete grouping/upsert boundary must supply/enforce `knownWorkerIds` or an eligible-worker set, then `knownWorkerIds?: Set<string>` with undefined/empty-set bypass is not enough.
- Tests that explicitly bless undefined/empty eligible sets are evidence against the AC unless the story narrowly scopes the helper as not live-write/upsert-ready and records that distinction.
- Acceptable correction patterns:
  - make the eligible set required and non-empty for the policy that claims write/upsert readiness; or
  - split pure grouping from a `prepareGroupedCartSessionForUpsert`/adapter boundary that requires a non-empty eligible set before producing/persisting grouped cart state.

3. Secret-safety tests do not inject secrets into echoed fields
- Absence checks against a static list on normal fixtures are weak. If the policy echoes `product_name`, `correlation_id`, owner IDs, references, messages, or candidate metadata, tests must inject representative secret-like values into those exact output-bearing fields.
- The implementation must reject, redact, or omit those values before they reach result/log payloads.

4. User-provided implementation summary is not canonical BMad evidence
- Even when the user provides passing test/typecheck summaries, inspect and reconcile the story artifact.
- If the story required Dev Agent Record / Evidence / File List / unverified surfaces and they are absent from the repo artifact, treat this as a completion-evidence blocker or at minimum an explicit artifact blocker.
- Continuation docs such as `CONTINUE-HERE.md` must be reconciled to the review result, not left at pre-dev status.

## Review evidence bundle
- Inspect story artifact, state.json, sprint-status.yaml, continuation docs, implementation, tests, and adjacent entry points/callers.
- Rerun focused package tests, package/workspace typecheck, artifact parses, and `git diff --check` when practical.
- Record runtime Redis/Electron/browser/vendor/checkout execution as unclaimed when the change is pure policy only.
