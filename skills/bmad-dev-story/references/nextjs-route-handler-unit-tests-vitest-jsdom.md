# Next.js route-handler unit tests with Vitest + jsdom

## Problem

In Vitest with `environment: "jsdom"`, `new Request()` is polyfilled and lacks the internal symbols that Next.js uses to parse cookies. When you do `new NextRequest(new Request(...))`, `nextRequest.cookies.get(...)` returns `undefined` even when the `Request` has a `cookie` header.

This makes behavior-level route tests for Next.js App Router routes difficult because:
- Route handlers expect `NextRequest` with working `cookies.get(...)`.
- Route handlers expect `nextUrl` with `searchParams`.
- Auth guards and Supabase SSR fail in unit context.

## Working pattern: lightweight mock NextRequest

Instead of constructing a real `NextRequest`, mock the dependencies and pass a plain object with the surface the route actually touches.

### Example: OAuth start/callback route tests

```ts
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

vi.mock("@/lib/auth/auth-guard", () => ({
  requireAuthedOwnerId: vi.fn(),
}));

vi.mock("@/lib/shopify/config", () => ({
  getShopifyConfig: vi.fn(),
}));

vi.mock("@/lib/shopify/service", async () => {
  const actual = await vi.importActual("@/lib/shopify/service");
  return {
    ...actual,
    buildOAuthStart: vi.fn(),
    handleOAuthCallback: vi.fn(),
  };
});

import { requireAuthedOwnerId } from "@/lib/auth/auth-guard";
import { getShopifyConfig } from "@/lib/shopify/config";
import { buildOAuthStart, handleOAuthCallback } from "@/lib/shopify/service";
import { GET as startGET } from "@/app/api/shopify/oauth/start/route";
import { GET as callbackGET } from "@/app/api/shopify/oauth/callback/route";

function makeNextRequest(
  url: string,
  cookieMap: Record<string, string> = {}
): unknown {
  const parsed = new URL(url);
  const cookies = new Map<string, { name: string; value: string }>();
  for (const [name, value] of Object.entries(cookieMap)) {
    cookies.set(name, { name, value });
  }
  return {
    url,
    nextUrl: parsed,
    cookies: {
      get(name: string) {
        return cookies.get(name);
      },
    },
  };
}

describe("GET /api/shopify/oauth/start", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    process.env.SHOPIFY_API_KEY = "test-api-key";
    process.env.SHOPIFY_API_SECRET = "test-api-secret";
  });

  afterEach(() => {
    delete process.env.SHOPIFY_API_KEY;
    delete process.env.SHOPIFY_API_SECRET;
  });

  it("returns 401 when auth guard throws", async () => {
    (requireAuthedOwnerId as ReturnType<typeof vi.fn>).mockRejectedValue(
      new Error("Not authenticated")
    );

    const res = await startGET(
      makeNextRequest("https://app.example.com/api/shopify/oauth/start?shopDomain=my-store.myshopify.com") as any
    );
    expect(res.status).toBe(401);
    const body = await res.json();
    expect(body.error).toMatch(/Not authenticated/);
  });

  it("returns 503 when Shopify config is missing", async () => {
    (requireAuthedOwnerId as ReturnType<typeof vi.fn>).mockResolvedValue(1);
    (getShopifyConfig as ReturnType<typeof vi.fn>).mockReturnValue({
      enabled: false,
      appUrl: undefined,
      scopes: ["read_products"],
      missing: ["SHOPIFY_API_KEY"],
    });

    const res = await startGET(
      makeNextRequest("https://app.example.com/api/shopify/oauth/start?shopDomain=my-store.myshopify.com") as any
    );
    expect(res.status).toBe(503);
    const body = await res.json();
    expect(body.error).toMatch(/not configured/i);
  });

  it("redirects to Shopify with httpOnly nonce cookie on valid request", async () => {
    (requireAuthedOwnerId as ReturnType<typeof vi.fn>).mockResolvedValue(42);
    (getShopifyConfig as ReturnType<typeof vi.fn>).mockReturnValue({
      enabled: true,
      appUrl: "https://app.example.com",
      scopes: ["read_products", "write_products"],
      missing: [],
    });
    (buildOAuthStart as ReturnType<typeof vi.fn>).mockReturnValue({
      redirectUrl: "https://my-store.myshopify.com/admin/oauth/authorize?client_id=test",
      sessionNonce: "nonce-abc-123",
    });

    const res = await startGET(
      makeNextRequest("https://app.example.com/api/shopify/oauth/start?shopDomain=my-store.myshopify.com") as any
    );

    expect(res.status).toBe(307);
    expect(res.headers.get("location")).toBe(
      "https://my-store.myshopify.com/admin/oauth/authorize?client_id=test"
    );

    const setCookie = res.headers.get("set-cookie") ?? "";
    expect(setCookie).toContain("shopify_oauth_nonce=nonce-abc-123");
    expect(setCookie).toContain("HttpOnly");
    expect(setCookie).toContain("SameSite=lax");
    expect(setCookie).toContain("Max-Age=600");
    expect(setCookie).toContain("Path=/");
  });
});

describe("GET /api/shopify/oauth/callback", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    process.env.SHOPIFY_API_KEY = "test-api-key";
    process.env.SHOPIFY_API_SECRET = "test-api-secret";
  });

  afterEach(() => {
    delete process.env.SHOPIFY_API_KEY;
    delete process.env.SHOPIFY_API_SECRET;
  });

  it("redirects to safe error page when auth guard throws", async () => {
    (requireAuthedOwnerId as ReturnType<typeof vi.fn>).mockRejectedValue(
      new Error("Not authenticated")
    );
    (getShopifyConfig as ReturnType<typeof vi.fn>).mockReturnValue({
      enabled: true,
      appUrl: "https://app.example.com",
      scopes: ["read_products"],
      missing: [],
    });

    const res = await callbackGET(
      makeNextRequest("https://app.example.com/api/shopify/oauth/callback?code=c&shop=s.myshopify.com&state=s") as any
    );

    expect(res.status).toBe(307);
    const loc = res.headers.get("location") ?? "";
    expect(loc).toContain("/shopify?error=");
    expect(loc).toContain(encodeURIComponent("Not authenticated"));
  });

  it("redirects to success with connected shop and clears nonce cookie", async () => {
    (requireAuthedOwnerId as ReturnType<typeof vi.fn>).mockResolvedValue(1);
    (getShopifyConfig as ReturnType<typeof vi.fn>).mockReturnValue({
      enabled: true,
      appUrl: "https://app.example.com",
      scopes: ["read_products"],
      missing: [],
    });
    (handleOAuthCallback as ReturnType<typeof vi.fn>).mockResolvedValue({
      shopDomain: "my-store.myshopify.com",
    });

    const res = await callbackGET(
      makeNextRequest(
        "https://app.example.com/api/shopify/oauth/callback?code=c&shop=my-store.myshopify.com&state=s",
        { shopify_oauth_nonce: "nonce-123" }
      ) as any
    );

    expect(res.status).toBe(307);
    const loc = res.headers.get("location") ?? "";
    expect(loc).toContain("/shopify?connected=");
    expect(loc).toContain(encodeURIComponent("my-store.myshopify.com"));

    const setCookie = res.headers.get("set-cookie") ?? "";
    expect(setCookie).toContain("shopify_oauth_nonce=");
    expect(setCookie).toContain("Max-Age=0");
    expect(setCookie).toContain("HttpOnly");
  });
});
```

## Key points

1. **Mock the auth guard and config** so the route handler doesn't depend on Supabase/cookies SSR.
2. **Mock service-layer functions** (`buildOAuthStart`, `handleOAuthCallback`) so you test route orchestration, not business logic.
3. **Use a plain object for `NextRequest`** with `url`, `nextUrl` (a real `URL` instance), and `cookies.get` (a `Map` lookup). This avoids jsdom's `Request` / `NextRequest` incompatibility.
4. **Assert on `res.status`, `res.headers.get("location")`, and `res.headers.get("set-cookie")`** for redirect and cookie behavior.
5. **Assert on mocked service function calls** with `toHaveBeenCalledWith(expect.objectContaining({...}))` to verify param passing.

## NextResponse.redirect requires absolute URLs

`NextResponse.redirect("/shopify?error=foo")` throws at runtime because Next.js validates the URL as absolute. In route handlers:
- Always construct absolute redirect URLs (e.g., `\${appUrl}/shopify?error=...`).
- If `appUrl` may be undefined in a missing-config branch, return `NextResponse.json({ error: "..." }, { status: 503 })` instead of a redirect.
