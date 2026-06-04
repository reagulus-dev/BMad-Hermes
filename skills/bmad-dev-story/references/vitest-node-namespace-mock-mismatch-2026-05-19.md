# Vitest node:* namespace mock mismatch pattern (2026-05-19)

## Context

During HLX-TECHDEBT-2, tests for `getNotificationSettings()` that mock `node:fs` were silently failing:
- `fsMock.readFileSync` was mocked, but `getNotificationSettings()` fell into its catch branch and returned defaults.
- Root cause: the mock shape did not match the import style.

## Pattern

Production code:

```ts
import * as fs from 'node:fs';
```

Common incorrect mock:

```ts
vi.mock('node:fs', () => ({ default: fsMock }));
```

This creates a default export, but `import * as fs` expects named exports.
Result: `fs.readFileSync` is undefined → calling it throws → caught → defaults used.

Correct mock:

```ts
const fsMock = {
  readFileSync: vi.fn(),
};

vi.mock('node:fs', () => fsMock);
```

This exposes `readFileSync` as a named export, matching `import * as fs`.

## Checklist

If a BMad test:
- mocks a `node:*` module (`node:fs`, `node:child_process`, etc.),
- but the code under test behaves as if the mock is not wired (falls back, throws, or uses real module),
then:
- verify the mock shape matches the import style:
  - `import * as X from 'node:fs'` → `vi.mock('node:fs', () => { readFileSync, ... })`
  - `import fs from 'node:fs'` → `vi.mock('node:fs', () => ({ default: { readFileSync, ... } }))`
