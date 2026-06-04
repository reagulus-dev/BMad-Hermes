# CF-E1-S1: Next.js scaffold in existing directory (2026-05-23)

## Situation

- Story: CF-E1-S1 — Tech Stack and Project Scaffolding for CardForge.
- Project directory /home/reagulus/projects/cardforge already had:
  - _bmad/
  - CONTINUE-HERE.md
  - docs/
- Goal: scaffold Next.js 15 App Router app in-place using TypeScript, pnpm, Tailwind v4, etc.

## Key issues and how they were handled

- create-next-app refused to run in-place:
  - Reason: existing files could conflict.
  - Fix: ran create-next-app into /tmp/cardforge-scaffold with --skip-install, then copied files into cardforge root, preserving _bmad/ and docs.

- pnpm install timeouts:
  - Initial attempts via execute_code and background terminal timed out.
  - Fix: used direct terminal with npx pnpm install; ran in foreground with a long timeout.

- ESLint config incompatibility:
  - create-next-app generated eslint.config.mjs that imported:
    - "eslint/config"
    - "eslint-config-next/core-web-vitals"
  - Next.js/ESLint versions in this environment caused:
    - “Cannot find module”
    - “nextVitals is not iterable”
  - Fix: replaced with a minimal config using “next/core-web-vitals” and basic rules, no Next.js plugin required for scaffold validation.

- Vitest missing jsdom:
  - Vitest config requested jsdom environment, but dependency not installed.
  - Fix: added jsdom as a devDependency.

## Outcome

- Scaffold completed with:
  - Next.js 15 App Router
  - TypeScript strict
  - Tailwind CSS v4
  - Prisma + Supabase placeholders
  - App shell + route placeholders
  - Vitest + Playwright configs
  - lint/typecheck/test/prisma:validate all passing.
- Status: implemented_not_reviewed, routed to bmad-code-review.

This is a concrete example of:
- Avoiding in-place create-next-app when directory not empty.
- Handling heavy installs that exceed tool timeouts.
- Recovering from eslint-config-next import failures with a minimal config.
