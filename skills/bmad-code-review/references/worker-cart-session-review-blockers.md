# Worker-owned cart/session state review blockers

Use this reference when a BMad story introduces worker-owned cart/session persistence, checkout-session state, or renderer display of cart/session state.

## Durable review lessons

### 1. Verify buildability at the package that imports the new boundary
If a pure package imports a workspace package for a type only, check the importing package's `package.json` dependency graph and run its own typecheck. A root/package test pass can miss `TS2307` when the new import is not resolvable from that package.

Review pattern:
- Inspect the changed package `package.json`.
- Run the changed package typecheck, not only the package that owns the exported type.
- If a pure orchestrator package imports DB types, require either an explicit workspace dependency or a narrow local/shared contract that preserves the intended package boundary.

### 2. Claimed focused tests require actual focused test files/cases
Do not accept a stable pre-existing test count as evidence for a new persistence boundary. Search for test files and test names tied to the new module/helper.

For worker cart/session stories, look for focused coverage such as:
- `workerCartSessions.test.ts` or equivalent repository tests.
- `cartSessionOwnership.test.ts` or equivalent pure validation tests.
- Required ownership fields missing/rejected.
- Duplicate worker/profile/cart-session rejection and error translation.
- Create/update behavior.
- Sensitive-value rejection/redaction/absence in all persisted payload surfaces.
- Deterministic psql args for read paths if parsing CLI output.

### 3. Redacting only top-level reference fields is insufficient
Cart/session payloads often include JSON arrays/objects (`target_items`, `cart_lines`, `item_attempts`) that may carry product metadata, operator notes, URLs, or accidental raw secrets. Review sensitive-data handling across the entire serialized state, not only `account_ref`, `shipping_ref`, and `payment_ref`.

Block when raw secret-like keys/values can be persisted in nested JSON, for example:
- `rawPaymentToken`, `rawCookieJar`, `rawCaptchaSolution`
- token/cookie/password/secret/authorization-like keys
- OTP/CAPTCHA/3DS/SCA values
- webhook URLs, connection strings, browser profile internals

### 4. Dynamic psql `--command` SQL needs safe quoting/parameterization
Thin psql-backed helpers must not interpolate arbitrary dynamic state directly into SQL. JSON payloads can contain quotes and arbitrary text; unsafe interpolation is both fragile and security-sensitive.

Review asks:
- Is there a helper for SQL literal escaping/JSON serialization?
- Are all dynamic values passed through it?
- Do tests include quotes/apostrophes and secret-like payloads?
- Are read helpers using deterministic `--tuples-only --no-align --field-separator` when parsing rows?

### 5. Worker ownership requires known-worker enforcement or an explicit tested boundary
A `worker_id TEXT NOT NULL` field plus uniqueness is not the same as proving the worker exists. If the implementation summary claims `worker_id references checkout_workers(worker_id)`, verify the migration actually contains the FK or that a repository/service boundary validates known workers with focused tests.

### 6. Renderer “model-backed” wording requires an invoked adapter path
For renderer cart/session panels, verify the data-loading path is actually used by the route:
- The loader is called before or during render/navigation.
- A preload/main/service adapter exists if the renderer references `window.<bridge>`.
- The adapter has a real source of worker identity/session keys; an adapter that iterates an empty local `knownWorkerIds` set will always return `[]` even when the DB contains rows.
- Tests exercise the bridge/adapter path or explicitly label the UI as contract-only/not runtime-backed.

Block when a loader is defined but never called, no bridge exists, or the bridge is called but necessarily returns empty local state while the UI says “model-backed”.

### 7. Fresh post-correction reviews must rerun the changed UI slice
After a BLOCKED worker-cart/session correction, do not rely only on the newly added DB/orchestrator focused tests. If the correction touches renderer navigation, checkout-worker UI, preload, or IPC, rerun the focused renderer tests for that route and inspect the failing case before recording a fresh verdict.

Specific regression checks from HLX-5.4-class corrections:
- Checkout-worker duplicate/required-profile validation tests still pass after adding cart/session loaders.
- The renderer loader is called on the actual navigation path and does not break existing route validation/state setup.
- IPC/main adapters can discover all relevant worker IDs from production state, not only from an optional in-memory set populated nowhere.
- Known-worker enforcement is present at a production boundary. A repository option such as `knownWorkerIds?: Set<string>` is insufficient unless a reviewed caller supplies it or DB constraints enforce it.
- JSONB fields serialized with `JSON.stringify(...)` are not interpolated into single-quoted SQL literals; include apostrophe/quote regression cases for nested JSON payloads.
- Sensitive-data handling is value-aware, not only key-name-aware: secret-like scalar values under safe-looking keys, `correlation_id`-like fields, URLs, cookies, tokens, OTP/CAPTCHA/SCA values, and payment/browser-session identifiers must be rejected/redacted according to the story’s policy.
