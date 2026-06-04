---
name: playwright-vitest-integration-fixes
description: >
  Common TypeScript type fixes when integrating Playwright with Vitest in a
  strict tsconfig (ES2022 target, NodeNext moduleResolution, strict mode).
---

# Playwright + Vitest Integration Fixes

## vi.hoisted() for Mock Hoisting

**Problem:** `vi.mock('playwright')` is hoisted to top of file, but mock objects defined as module-level `const` are not initialized yet, causing `ReferenceError: Cannot access 'mockChromium' before initialization`.

**Fix:** Use `vi.hoisted()` to create mock objects in the hoisted scope:

```ts
const { mockBrowserContext, mockChromium } = vi.hoisted(() => {
  const ctx = {
    close: vi.fn().mockResolvedValue(undefined),
    on: vi.fn(),
    once: vi.fn(),
  } as unknown as ReturnType<typeof import('playwright').chromium['launchPersistentContext']>;

  const chromium = {
    launchPersistentContext: vi.fn().mockResolvedValue(ctx),
    launch: vi.fn().mockResolvedValue({
      contexts: () => [ctx],
      close: vi.fn().mockResolvedValue(undefined),
    }),
  } as const;

  return { mockBrowserContext: ctx, mockChromium: chromium };
});

vi.mock('playwright', () => ({
  chromium: mockChromium,
}));
```

**Why it works:** `vi.hoisted()` runs in the same hoisted scope as `vi.mock()`, so the mocks are available when the module factory executes.

## Extracting BrowserContext from Browser.launch()

**Problem:** `chromium.launch()` returns `Browser`, not `BrowserContext`. Calling `browser.on('close', ...)` fails because `Browser` only emits `"context"` and `"disconnected"` events, not `"close"`.

**Fix:** Extract the `BrowserContext` from `Browser.contexts()[0]`:

```ts
const browser = await chromium.launch(launchOpts);
const context = browser.contexts()[0];

context.on('close', () => {
  rmSync(tempDir, { recursive: true, force: true });
});

return context;
```

## MapIterator Iteration in ES2022

**Problem:** `tsconfig.base.json` targets ES2022. Iterating `Map.entries()` or `Map.values()` with `for...of` requires ES2015+ or `--downlevelIteration`.

**Fix:** Use `Array.from()` for iteration:

```ts
// Instead of:
for (const [, meta] of registry) {

// Use:
for (const [, meta] of Array.from(registry.entries())) {
```

## Default Module Import with NodeNext

**Problem:** `"module": "NodeNext"` requires explicit `esModuleInterop: true` (or explicit `import * as os from 'os'`) for default imports. `import os from 'node:os'` may fail with `Module '\"node:os\"' has no default export`.

**Fix:** Use named imports for Node builtins:

```ts
// Instead of:
import os from 'node:os';
// Use:
import { tmpdir } from 'node:os';
```

## Removing Unused Type Imports

**Problem:** Strict mode with `noUnusedLocals` flags unused type imports like `ProfileStatus`, `SANITIZED_NAME_PATTERN`, or aliased types.

**Fix:** Audit imports before running typecheck:
- Remove types only imported but never referenced
- Remove constants only imported but never used
- Keep types exported from `index.ts` even if not used internally (they're part of the public API)
