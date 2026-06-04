# Electron Renderer Static View Pattern (HLX-3.2)

## Context

- Project: Helix
- Story: HLX-3.2 (Build Vendor Modules UI)
- Date: 2026-05-15

## Problem

- A UI story requires rendering data from a workspace package (e.g., @helix/vendors).
- The renderer is sandboxed:
  - nodeIntegration: false
  - contextIsolation: true
  - sandbox: true
- Direct imports of Node/DB modules in the renderer are forbidden.
- Build/runtime wiring (bundler + IPC) for direct @helix/* imports into the renderer is not yet ready.

## Pattern

Use a static registry mirror in the renderer as a temporary data source:

- In renderer-only files (e.g., nav-init.js):
  - Define a const array/object (e.g., VENDOR_MODULES) that mirrors the shape from the canonical package.
  - Add a comment:
    - “In a later story, this will be wired to @helix/vendors via IPC.”
- Use this mirror as the single source of truth for the renderer view:
  - List items
  - Detail panels
  - Status chips
- Ensure:
  - No Node/DB imports.
  - No preload/IPC assumptions that aren’t yet wired.
  - Values and semantics match the canonical package and UX artifacts.

## Validation

- Run:
  - pnpm typecheck
  - pnpm build
- Confirm:
  - The actual renderer entry used by BrowserWindow (e.g., index.html → nav-init.js) is updated.
  - There are no new TypeScript errors.
- Runtime:
  - Electron launch verification (Xvfb/CDP or manual) is preferred but may be deferred to code review/QA if not immediately available.
  - Do not claim runtime-verified without evidence.

## When to Replace

This is a temporary pattern. A future story must:
- Wire the renderer to the real registry via:
  - A main-process service
  - A preload IPC bridge
- Remove the static mirror or reduce it to dev-only fallback data.
