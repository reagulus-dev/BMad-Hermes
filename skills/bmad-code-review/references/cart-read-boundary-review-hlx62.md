# HLX-6.2 Cart-Read Boundary Review Pattern

Use this reference when reviewing add-to-cart boundary changes that capture post-ATC cart-line state and persist or emit that state for future guardrails.

## Blocking patterns found in HLX-6.2

### Artifact integrity can be a blocker even when code validation passes

If the story artifact still says `ready_for_dev`, lacks the required Dev Agent Record / Evidence / File List, or sprint status contains duplicate entries for the same story, do not pass the review just because tests pass.

Required handling:
- Append the review findings to the story artifact.
- Reconcile story frontmatter, `_bmad/state.json`, `_bmad/sprint-status.yaml`, and continuation docs to the real verdict.
- In `_bmad/sprint-status.yaml`, collapse duplicate story entries into one canonical block before final validation.
- Parse JSON/YAML and run `git diff --check` before committing the review artifact update.

### Vendor context must be preserved/derived, not re-hardcoded

When a prior story accepted a temporary single-vendor hardcode as a scoped note, later cart-read/persistence work must not deepen that assumption.

Block when:
- `vendor_module` is hardcoded again in the ATC/cart-read boundary.
- Grouped/cart-line types do not carry vendor context, making preservation impossible.
- Tests only cover the happy Pokémon Center path and do not prove unsupported/cross-vendor behavior or no-attempt behavior.

Correction shape:
- Carry `vendor_module` through grouping/candidate/output types or derive it from an explicit owner/context field.
- Reject mixed/unsupported vendor contexts before ATC/cart-read/persistence.
- Add focused tests for supported vendor and unsupported/mixed vendor behavior.

### Unknown and unreliable price are separate obligations

If the AC requires unknown **and unreliable** price outcomes, typing an `unreliable` union member is not enough.

Block when:
- The implementation never produces an unreliable price state.
- `unreliable_count` exists but is never incremented.
- Tests cover unknown/not-added behavior but not unreliable observed-price behavior.

Correction shape:
- Add a deterministic fixture/mock path that emits an unreliable price state with a reason.
- Increment reliability summaries accordingly.
- Test unknown price is not `0`/pass, and unreliable price is explicit and not treated as guardrail-passing.

### Persistence-before-progression must be meaningful

If the story says captured cart lines are persisted before downstream progression, optional hooks and swallowed persistence errors are not enough.

Block when:
- `upsertWorkerCartSession` or equivalent persistence is optional for a path that returns completion.
- Persistence exceptions are swallowed while returning `atc_completed` / success-like status.
- Tests assert only that a hook was called, without proving worker-cart-session redaction/known-worker enforcement through the actual boundary.

Correction shape:
- Make persistence failure visible in the result and/or prevent downstream progression claims when persistence fails.
- Exercise the actual DB/repository helper or a faithful injected boundary that enforces known-worker and redaction semantics.
- Add tests for ownership mismatch rejection and secret-like value redaction/absence in persisted cart lines/events.

## Verdict guidance

Use `BLOCKED` when any of the above violate explicit ACs or carry-forward notes. Passing focused tests/typechecks are useful evidence but do not override missing AC coverage or inconsistent BMad artifacts.
