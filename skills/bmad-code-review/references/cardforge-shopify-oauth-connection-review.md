# CardForge Shopify OAuth connection review pattern (CF-E4-S2)

Use this when reviewing a story that adds Shopify OAuth start/callback plumbing, token encryption, owner-scoped connection persistence, and dashboard connection status without live Shopify publishing/webhook/order behavior.

## Story contract signals

A Shopify OAuth connection story usually claims:
- authenticated/owner-resolved OAuth start route;
- normalized Shopify shop-domain validation;
- signed, expiring, owner/session-bound OAuth state, commonly paired with an httpOnly nonce cookie;
- Shopify callback HMAC verification before token exchange;
- token exchange behind a mocked/testable fetch boundary;
- encrypted access-token persistence only;
- owner-scoped connection read/upsert/disable paths;
- client-facing connection status that never exposes plaintext or encrypted tokens;
- safe dashboard states for missing config, configured-not-connected, connected, and disabled;
- no live Shopify success claims unless real dev-store credentials were exercised.

## Blocker checks

Block when any of these are true:

1. **Token encryption key validation is only non-empty.**
   - If the story requires key shape/length validation and fail-closed invalid-key behavior, a helper that accepts any non-empty `SHOPIFY_TOKEN_ENCRYPTION_KEY` and derives an AES key from it is not enough.
   - Require focused tests for missing key and invalid/weak/wrong-shape non-empty keys.

2. **Owner-scoped connection persistence lacks focused tests.**
   - Source inspection is not enough for a token/owner persistence boundary when the story explicitly required focused coverage.
   - Require tests proving owner id appears in repository query/update/upsert boundaries and that guessed IDs/shop domains cannot update another owner’s connection.

3. **Client status can expose secrets or lacks no-secret tests.**
   - `getConnectionStatus`/dashboard data must not include `access_token_encrypted` or plaintext tokens.
   - Require a no-secret status-return test when the story calls this out.

4. **Routes/callback are not tested at the boundary.**
   - Require focused route/service tests for OAuth start redirect URL + nonce cookie behavior, invalid/missing shop handling, missing config behavior, missing nonce, missing/tampered/expired/wrong-owner/wrong-session state, invalid HMAC, token exchange failure, and safe app-local redirect outcomes where practical.
   - Static route-export checks such as “`GET` exists” are not route-boundary evidence. For stories that explicitly name `GET /api/shopify/oauth/start` or `GET /api/shopify/oauth/callback`, require behavior-level handler tests or an equivalent exercised boundary that proves authenticated-owner resolution, missing-config handling, invalid-domain response, redirect target, httpOnly nonce cookie set/clear semantics, missing-nonce callback redirect, success redirect, and safe app-local error redirects.
   - Do not accept a correction record that says heavy route tests were avoided unless the remaining service tests genuinely prove the route-owned cookie/redirect/auth behavior. Service tests can complement route tests; they do not replace route tests for route-specific semantics.

5. **HMAC or state ordering is wrong.**
   - HMAC must be verified before token exchange/persistence.
   - State must bind owner + session nonce + shop domain and expire.

6. **Live Shopify verification is overclaimed.**
   - Passing mocked OAuth/unit tests does not prove a real dev-store connection.
   - Use PASS WITH NOTES or BLOCKED depending on the story’s claim; if live OAuth is out of scope and clearly unclaimed, record it as an unverified note, not a blocker.

## Evidence to ask for

- Focused OAuth helper/crypto tests: domain normalization, state valid/tampered/expired/wrong-owner/wrong-session, HMAC valid/invalid, token exchange success/failure with mocked fetch, encryption round-trip/tamper/missing-key/invalid-key.
- Focused repository/service tests: owner-scoped where clauses, upsert/read/disable scoping, no-secret connection status, encrypted-only persistence.
- Route tests or equivalent service-boundary tests: start route auth/config/domain/redirect/cookie, callback missing nonce, invalid HMAC/state, token exchange failure, success persistence.
- Full validation bundle: prisma validate/generate if touched, typecheck, lint, full tests, build route output, git diff --check.

## Verdict guidance

- **BLOCKED** when token encryption key validation fails the explicit story contract or required focused owner/route tests are absent despite broad validation passing.
- **PASS WITH NOTES** when static OAuth/security/owner boundaries are implemented and focused tests exist, but live Shopify dev-store verification remains out of scope/unverified.
