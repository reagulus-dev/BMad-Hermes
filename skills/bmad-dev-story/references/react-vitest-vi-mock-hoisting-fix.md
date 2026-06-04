# React + Vitest vi.mock Hoisting Fix

## Problem

`vi.mock()` is hoisted above all imports in Vitest. If the mock factory references variables that are defined in the same file (e.g., shared mock data), you get:

```
ReferenceError: Cannot access 'mockChromium' before initialization
```

Because `mockChromium` hasn't been declared yet at hoist time.

## Pattern

```ts
// BAD — ReferenceError
vi.mock('playwright', () => {
  const mockChromium = { ... }; // Not yet defined when factory runs
  return { chromium: mockChromium };
});

const { mockChromium } = vi.hoisted(() => ({ mockChromium: {} }));
// Now use mockChromium in vi.mock factory
```

```ts
// GOOD — Use vi.hoisted() for shared mock state
const { mockChromium } = vi.hoisted(() => ({
  mockChromium: {
    launchPersistentContext: vi.fn(),
    launch: vi.fn(),
  },
}));

vi.mock('playwright', () => ({
  chromium: mockChromium,
}));
```

## Why

Vitest hoists `vi.mock()` calls to the top of the file (like `import` statements). The factory function runs before the rest of the module body executes. Variables defined below the `vi.mock()` call are in the temporal dead zone.

`vi.hoisted()` explicitly declares variables at hoist time, making them available to the `vi.mock()` factory.

## When This Appears

This pattern shows up in:
- Delegated dev-story tasks for frontend/TSX files
- Electron app test files with Playwright/Cypress mocks
- Any Vitest file with `vi.mock()` that references shared mock data structures

## Source

Observed during Helix HLX-2.2 implementation: vi.mock was hoisted but mockChromium wasn't yet defined, causing test failures. Fixed by wrapping shared mocks in `vi.hoisted()`.
