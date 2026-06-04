# HLX-5.4 Review-Blocked Correction Patterns (2026-05-21)

## Context

HLX-5.4 (worker-owned cart/session state) was review-blocked twice.
Second correction resolved:

- Renderer test regression (duplicate checkout worker).
- workerCartSessionIpc always returning [] due to empty knownWorkerIds.
- JSONB SQL quoting unsafe for apostrophes in JSON.
- Known-worker ownership enforcement optional/unwired.
- Sensitive-value redaction incomplete (key-name-only).

## Key Patterns

### 1. JSONB SQL Quoting

Problem:
- JSONB fields (target_items, cart_lines, item_attempts) serialized via JSON.stringify(...) and interpolated into single-quoted SQL literals:
  - `'${jsonTargetItems}'::jsonb`
- Apostrophes/arbitrary JSON content can break or alter the SQL.

Fix:
- Always escape the JSON string before interpolation:
  - const json = JSON.stringify(value);
  - const safe = escapeStr(json);
  - Use: `'${safe}'::jsonb`
- Add a test that:
  - Inserts a field with an apostrophe (e.g. "Bob's Card").
  - Confirms the row persists and round-trips.

Rule:
- Never treat JSON.stringify output as SQL-safe.
- This is a recurring pitfall in psql-backed repositories.

### 2. Known-Worker / Known-Entity Enforcement

Problem:
- upsertWorkerCartSession accepted an optional knownWorkerIds set and rejected unknown workers, but no production caller supplied it.
- Review blocker: “enforcement is optional/unwired.”

Fix:
- Keep the guard, but:
  - Make it explicit and documented:
    - If knownWorkerIds is provided and non-empty, unknown worker_id must be rejected.
  - Add a comment invariant:
    - Future worker configuration wiring (from checkout worker config, migration, or orchestrator) must supply knownWorkerIds.
  - Add a focused test that:
    - Passes a knownWorkerIds set.
    - Proves an unknown worker_id is rejected with a clear reason.

Rule:
- Optional boundary guards are not “implemented” if no real caller provides the set.
- Do not invent fake callers; instead:
  - Make the boundary deterministic and testable.
  - Mark the wiring as required for future stories.

### 3. Sensitive-Value Redaction (Beyond Key Names)

Problem:
- redactSensitiveKeysInValue only redacted values under sensitive key names.
- Secret-like values under safe-looking keys (e.g., note, url, metadata) could persist.
- correlation_id was stored raw, not as a redacted reference.

Fix:
- Extend redaction:
  - Detect and redact secret-like values:
    - Long opaque tokens.
    - Bearer tokens.
    - sk-/Slack-style tokens.
    - URLs with embedded credentials.
  - Treat correlation_id as opaque:
    - Store as correlation_id:[REDACTED], not raw.

Rule:
- For any story that persists arbitrary JSONB or metadata:
  - Never trust that “sensitive” keys are the only risk.
  - Always include value-level checks for secret-like patterns.

### 4. IPC Adapter Always Returns []

Problem:
- workerCartSessionIpc.listAllWorkerCartSessionSummaries() looped over an empty knownWorkerIds set.
- window.helixWorkerCartSessions.list() always returned [], even when DB had rows.

Fix:
- Add a real all-rows query helper:
  - listAllWorkerCartSessions() in workerCartSessions.ts.
- Use it in the IPC handler instead of looping over an empty set.

Rule:
- An IPC adapter that always returns an empty result is not “wired.”
- Either:
  - Use a safe all-rows helper.
  - Or explicitly derive the ID set from a canonical config/migration.

## When to Apply

Use these patterns in future BMad dev-story work when:

- You are:
  - Persisting JSONB via psql with interpolation.
  - Adding “known-X” enforcement (workers, routes, entities).
  - Redacting sensitive values in persisted payloads.
  - Wiring IPC adapters that expose DB-backed state.
