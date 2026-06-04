# CF-E4-S2 correction: Vitest + Next.js route tests and crypto key tests

## Context

- Story: CF-E4-S2 — Shopify OAuth Connection.
- Initial review BLOCKED:
  - Token encryption key validation too weak.
  - Missing focused tests for repository/service/route behavior.
- Correction scope: enforce key validation, add focused tests, keep no-live-network rule.

## Key learnings

1) Next.js route handlers in Vitest:
   - Invoking GET from app/api/... with plain Request objects:
     - Fails or behaves unpredictably due to:
       - Missing NextRequest shape (cookies, nextUrl).
       - Supabase SSR / auth-guard returning 401/500 in unit context.
     - Leads to misleading “route tests” that reflect environment noise, not your logic.
   - Better:
     - Test your service/repo with mocks (owner scoping, OAuth flows, error paths).
     - For routes:
       - Static checks only:
         - Confirm GET/POST export.
         - Confirm imports from expected modules.

2) Crypto/OAuth key validation tests:
   - A common mistake: using a test key that doesn’t actually violate the rule it’s meant to test.
   - Example:
     - Test named “throws when key is all letters” using a key like:
       - "abcdefghijklmnopqrstuvwxyz123456"
       - This has digits → not “all letters” → test is a false positive.
   - Fix:
     - Ensure test values are aligned with the exact validation rule.
     - For “all letters”: only A-Z/a-z.
     - For “too short”: shorter than enforced minimum.

3) Mocking exchangeAccessToken:
   - Use vi.mock on the oauth module to control exchangeAccessToken.
   - Pattern:
     - vi.mock("@/lib/shopify/oauth", async () => {
         const actual = await vi.importActual("@/lib/shopify/oauth");
         return {
           ...actual,
           exchangeAccessToken: vi.fn(),
         };
       });
   - Then:
     - (oauthMod.exchangeAccessToken as ReturnType<typeof vi.fn>).mockResolvedValue({ ... });

## Outcome

- After correction:
  - prisma:validate, prisma:generate, typecheck, lint: PASS
  - test: 276/276 PASS (19 files)
  - build: PASS
  - git diff --check: PASS
- Story moved to implemented_not_reviewed; next workflow: bmad-code-review.
