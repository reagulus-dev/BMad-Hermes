# CardForge route-behavior test typecheck pitfall

Use this when reviewing Next.js route-handler behavior tests added as BMad evidence, especially OAuth/auth/callback routes.

## Session-derived pitfall

A correction can add useful behavior-level Vitest tests that execute and pass, while still failing the story's static validation gate because the route test helper does not typecheck against the route handler signature.

Concrete pattern seen in CF-E4-S2:

```ts
function makeNextRequest(...): unknown {
  return {
    url,
    nextUrl: new URL(url),
    cookies: { get(name: string) { ... } },
  };
}

await startGET(makeNextRequest("https://app.example.com/..."));
```

The focused Vitest run passed, full `pnpm test` passed, lint passed, and `next build` passed, but `corepack pnpm run typecheck` failed with TS2345 because `unknown` is not assignable to `NextRequest` for every route-handler call.

## Review rule

- Do not accept route-behavior test additions based on passing Vitest alone.
- Always run the project typecheck after adding or reviewing tests that use lightweight mocked `NextRequest` / route request objects.
- If `typecheck` fails only because the test helper is typed too broadly, treat it as a tiny static-validation blocker, not as a substantive OAuth/security blocker.
- Required correction should preserve the behavior coverage while fixing the helper typing, e.g. by returning a narrow local structural type cast at the call boundary or a properly typed compatible request object.

## Verdict guidance

Use `BLOCKED` when the story contract includes `typecheck PASS` and the fresh typecheck fails, even if:
- focused route tests pass,
- full Vitest suite passes,
- lint passes,
- build passes.

On the fresh re-review after the tiny typing correction, keep the scope tight: confirm the typecheck is clean, focused route tests still pass, and prior substantive source/security blockers remain resolved.
