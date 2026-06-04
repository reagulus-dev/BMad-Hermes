# Next.js Secure OAuth Integration Pattern

> Session: CF-E4-S2 (CardForge Shopify OAuth), 2026-05-31.
> Validated stack: Next.js 15 App Router, TypeScript strict, Vitest, Prisma, Supabase Auth.

## When to Use

Any story that wires a third-party OAuth flow (Shopify, Stripe Connect, Xero, etc.) into a Next.js app where:
- The app already has auth/owner scoping (e.g., Supabase + `requireAuthedOwnerId()`).
- Tokens must be encrypted at rest.
- Callbacks must be verified against replay/tampering.
- Tests must not hit live OAuth endpoints.

## Module Layout

```text
src/lib/<provider>/config.ts         # env guard, scopes, enabled check
src/lib/<provider>/oauth.ts          # pure helpers: domain normalize, state, HMAC, token exchange
src/lib/<provider>/crypto.ts         # server-only AES-GCM encryption
src/lib/<provider>/repositories.ts   # owner-scoped DB access
src/lib/<provider>/service.ts        # orchestration: buildOAuthStart, handleOAuthCallback, getConnectionStatus
src/lib/<provider>/schemas.ts        # Zod input validation
src/app/api/<provider>/oauth/start/route.ts
src/app/api/<provider>/oauth/callback/route.ts
src/app/(dashboard)/<provider>/page.tsx
src/app/(dashboard)/<provider>/<Provider>Client.tsx
```

## Key Implementation Rules

### 1. Domain normalization (pure, testable)

```ts
export function normalizeShopDomain(input: string): string | null {
  const trimmed = input.trim().toLowerCase();
  if (!trimmed) return null;
  let hostname = trimmed;
  if (hostname.includes("://")) {
    try { hostname = new URL(hostname).hostname; } catch { return null; }
  }
  const portIdx = hostname.indexOf(":");
  if (portIdx !== -1) hostname = hostname.slice(0, portIdx);
  if (!hostname.endsWith(".myshopify.com")) return null;
  const subdomain = hostname.slice(0, -".myshopify.com".length);
  if (!subdomain || subdomain.includes(".") || subdomain.includes("/")) return null;
  return hostname;
}
```

Always reject non-matching domains before building redirect URLs. Never let user input flow directly into a URL.

### 2. Signed, expiring, owner-bound state

Use HMAC-SHA256 over a JSON payload containing owner id, session nonce, shop domain, and expiry timestamp. Encode as `base64url(payload).base64url(signature)`.

```ts
export function createOAuthState(params: {
  ownerId: number;
  sessionNonce: string;
  shopDomain: string;
  secret: string;
  expiresInSeconds?: number;
}): string { ... }

export function verifyOAuthState(params: {
  state: string;
  ownerId: number;
  sessionNonce: string;
  secret: string;
  nowSeconds?: number;
}): { ownerId; sessionNonce; shopDomain; expiresAt } | null { ... }
```

- `sessionNonce` must be stored in an **httpOnly cookie** on start and checked on callback.
- Reject tampered, expired, wrong-owner, and wrong-nonce state.

### 3. Callback HMAC verification

Canonicalize query params by sorting keys, joining `key=value` with `&`, excluding `hmac`. Compare with `timingSafeEqual`.

```ts
export function verifyCallbackHmac(query: Record<string, string>, apiSecret: string): boolean {
  const { hmac, ...rest } = query;
  if (!hmac) return false;
  const message = Object.keys(rest).sort().map(k => `${k}=${rest[k]}`).join("&");
  const expected = createHmac("sha256", apiSecret).update(message).digest("hex");
  if (hmac.length !== expected.length) return false;
  return timingSafeEqual(Buffer.from(hmac, "hex"), Buffer.from(expected, "hex"));
}
```

### 4. Token exchange boundary (injectable fetch)

```ts
export async function exchangeAccessToken(params: {
  shopDomain: string; code: string; apiKey: string; apiSecret: string; redirectUri: string;
  fetchImpl?: typeof fetch;
}): Promise<{ accessToken: string; scope: string }> { ... }
```

Always accept `fetchImpl` so tests can mock the network layer. No normal test should hit a live OAuth endpoint.

### 5. Token encryption (server-only)

Use AES-256-GCM with a per-encryption random salt and IV. Derive the key with `scryptSync` from `SHOPIFY_TOKEN_ENCRYPTION_KEY` (or provider equivalent).

```ts
// server-only
export function encryptToken(plaintext: string): string { ... }
export function decryptToken(ciphertext: string): string { ... }
```

- Never persist plaintext tokens.
- Never return encrypted tokens to the client.
- Fail closed if the encryption key env var is missing.

### 6. Owner-scoped repository

```ts
export const shopifyConnectionRepo = {
  getForOwner: async (ownerId) => { ... },
  upsertForOwner: async (ownerId, { shopDomain, accessTokenEncrypted, scopes }) => { ... },
  disableForOwner: async (ownerId) => { ... },
};
```

Always include `owner_id` in `where` clauses. Upsert must not update another owner's connection.

### 7. Service orchestration

```ts
export function buildOAuthStart({ ownerId, shopDomainRaw, appUrl, apiKey, apiSecret }):
  { redirectUrl: string; sessionNonce: string }

export async function handleOAuthCallback({ ownerId, sessionNonce, query, apiSecret, apiKey, redirectUri }):
  Promise<{ shopDomain: string }>

export async function getConnectionStatus(ownerId): Promise<ConnectionStatus>
```

`getConnectionStatus` must never return `access_token_encrypted`.

### 8. Route handlers

**Start route:**
- `requireAuthedOwnerId()` first.
- Check provider config is enabled.
- Validate `shopDomain` input with Zod.
- Call `buildOAuthStart()`, set httpOnly nonce cookie, redirect to provider.

**Callback route:**
- `requireAuthedOwnerId()` first.
- Read nonce from cookie; reject if missing.
- Call `handleOAuthCallback()`.
- On success: clear nonce cookie, redirect to dashboard with `?connected=...`.
- On error: redirect to dashboard with `?error=...`.

### 9. Dashboard UI states

Render four states without crashing:
1. **Missing config** — setup checklist, no connect action.
2. **Configured, not connected** — shop domain input + Connect button.
3. **Connected** — shop domain, scopes, timestamp. No secrets.
4. **Disabled** — disabled timestamp, reconnect guidance.

Never show "syncing", "published", "orders imported" unless that feature is actually implemented.

## Testing Strategy

Add a focused unit test file:

```text
tests/unit/<provider>-oauth-crypto.test.ts
```

Cover:
- Domain normalization: valid, URL-with-path, whitespace, non-matching, empty, extra dots.
- State: round-trip, tampered, expired, wrong owner, wrong nonce, malformed.
- HMAC: valid recomputed HMAC, missing hmac, wrong hmac.
- Token exchange: success (mocked fetch), non-ok response, missing access_token.
- Encryption: round-trip, different ciphertext for same plaintext, tampered ciphertext, missing key.

Avoid mocking Prisma for the OAuth layer; test pure helpers directly. Route-level behavior can be validated indirectly (file presence, typecheck, build emission).

## Pitfalls

- **Do not** use `NEXT_PUBLIC_SUPABASE_URL` as the app origin for redirect URIs. Use `NEXT_PUBLIC_APP_URL` or derive from request headers.
- **Do not** return encrypted tokens or API secrets in any client-facing data.
- **Do not** skip HMAC verification before exchanging the code.
- **Do not** allow the callback to proceed without a matching session nonce cookie.
- **Do not** claim live OAuth success unless a real development store/account was exercised. Mocked tests prove boundary behavior only.
- **Do not** rename Prisma columns just because the semantic unit changed (e.g., `_pence` → `_millipence`). Rename requires a second migration; the label is acceptable.
