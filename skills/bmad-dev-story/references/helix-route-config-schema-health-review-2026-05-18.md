# HLX-3.5 Route Config Schema Alignment and Health Metadata Review (2026-05-18)

## Context

A resumed BMad dev-story correction for HLX-3.5 had route/proxy configuration UI, preload, service, and DB code mostly implemented. A fresh review after the correction found issues that normal typecheck/build did not fully protect against.

## Findings

- Physical DB schema vs repository/public API mismatch:
  - The legacy `network_configs` table used `label` as the physical column, while the repository/UI contract exposed `name`.
  - The physical table also still required `route_reference`.
  - A repo method that writes only the public shape can pass TypeScript while failing migration/live DB behavior or returning rows with wrong fields.
- Nondeterministic placeholder health metadata:
  - A `runHealthCheck()` placeholder used random status/latency.
  - Random health values make tests flaky and can mislead operators into thinking a real network probe happened.

## Durable Pattern

For DB-backed Electron route/config stories:

1. Verify physical schema requirements after migrations, not just repository TypeScript types.
2. Map legacy/private DB columns explicitly at the repository boundary, e.g. `label AS name`, and write required physical fields such as `label` and `route_reference` even when the public contract says `name`.
3. Add or update migrations to align schema expectations rather than relying on accidental compatibility.
4. Keep placeholder runtime checks deterministic and honestly labeled:
   - Local/synthetic route can return a stable healthy/low-latency value.
   - Configured routes should default to `unknown` unless a real probe or explicit test/dev override exists.
5. Add focused repository tests and, where practical, a live DB smoke that creates/lists/deletes a safe QA row through the built helpers.
6. Keep Electron/Xvfb runtime QA separate from service/repository smoke. Do not claim full Electron runtime proof when only DB/service and unit tests ran.

## Evidence Shape Used

- `pnpm run db:migrate`
- targeted DB repository Vitest tests
- targeted desktop route/nav Vitest tests
- workspace typecheck/test/build
- live DB repository smoke through built `@helix/db` helpers: create route row, list and verify public shape, delete QA row

## Reporting Lesson

A correction can pass code review with notes when schema alignment and deterministic placeholders are fixed and validated, but if real Electron runtime/Xvfb route QA is not run, route next to `bmad-qa-gate` and state the runtime evidence boundary explicitly.
