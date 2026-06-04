# Supabase SSR `setAll` Signature Review Pitfall

Use when reviewing Next.js App Router stories that use `@supabase/ssr` server clients for auth-changing operations such as sign-out, token refresh, callback handling, or session cookie updates.

## Durable lesson

For the installed `@supabase/ssr` contract, the server cookie adapter's modern setter is called as:

```ts
setAll(cookieArray)
```

not:

```ts
setAll({ cookies: cookieArray })
```

A wrapper-shaped implementation can typecheck if locally typed too loosely, and source-regex tests that only look for the string `setAll` will pass, but runtime sign-out/session updates can fail when the package calls `setAll(removeCookies.map(...))` and the app tries to iterate `allCookies.cookies`.

## Review checks

- Inspect `src/lib/auth/server.ts` or equivalent Supabase server-client factory.
- Compare the adapter implementation against the installed package, not just docs memory:
  - `node_modules/@supabase/ssr/dist/module/types.d.ts` should define `SetAllCookies` as an array callback.
  - `node_modules/@supabase/ssr/dist/module/cookies.js` should show runtime calls like `setAll(allToSet)` and `setAll(removeCookies.map(...))`.
- Accept shapes like:

```ts
setAll(cookiesToSet) {
  for (const { name, value, options } of cookiesToSet) {
    cookieStore.set(name, value, options);
  }
}
```

- Block shapes like:

```ts
setAll(allCookies) {
  for (const cookie of allCookies.cookies) {
    cookieStore.set(cookie.name, cookie.value, cookie.options);
  }
}
```

unless the installed package version explicitly calls that wrapper shape.

## Evidence expectations

Do not accept tests that merely assert `server.ts` contains `setAll`, `set`, or `remove`. Require a focused regression that would fail for the wrapper-shaped bug, for example:

- export a tiny cookie-adapter factory and call its `setAll([{ name, value, options }])` directly in a unit test; or
- mock `createServerClient` and capture/invoke the provided cookie adapter with an array; or
- exercise the sign-out route/action through a mocked Supabase SSR storage callback that calls `setAll(cookieArray)`.

Source-regex tests can remain as guardrails for wrong-host regressions, but they are not enough for cookie adapter contract behavior.

## Verdict guidance

Use `BLOCKED` when a story acceptance criterion requires signed-in users to sign out or server-side auth mutation to persist, and the cookie adapter uses the wrong `setAll` runtime signature or lacks behavior-level regression coverage. Static validation passing does not prove cookie clearing works.
