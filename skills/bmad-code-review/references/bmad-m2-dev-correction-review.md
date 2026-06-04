# BMad M2.7 Dev-Correction Then Local Review Pattern

Use when the user asks to commit current work, delegate `bmad-dev-story correction` to a cheaper MiniMax/M2.x subagent, and then have Alice perform the fresh BMad code review.

## Pattern

1. Commit the current reviewed/reconciled state first if the user explicitly asks to commit everything before correction.
2. Delegate only the dev-story correction to M2.x. The subagent is an implementer, not the progression-gate reviewer.
3. When the subagent returns or exits:
   - Inspect `git status`, the modified files, and validation output.
   - If the subagent left type/test failures, finish the smallest correction necessary to reach a reviewable state rather than accepting its partial result or reclassifying the story as blocked solely because the implementer stopped early.
   - Keep attribution clear in the story record: M2.x performed the correction attempt; Alice performed follow-up fixes and the fresh code review.
4. Run the fresh review yourself with the full validation bundle and artifact parsing.
5. Reconcile story frontmatter/body, `_bmad/state.json`, `_bmad/sprint-status.yaml`, and continuation docs to the fresh verdict.
6. Commit the final correction + review artifacts together when the user requested a clean committed state.

## Validation command recording

Some validation tools need a syntactically valid URL even when they do not connect to the database. For Prisma schema validation, a dummy URL such as `postgresql://localhost/cardforge` may be used at runtime. In durable BMad artifacts, record it as:

```bash
DATABASE_URL=[REDACTED] corepack pnpm exec prisma validate
```

Do not persist credential-like placeholder URLs (`postgresql://user:***@...`) in story artifacts, sprint status, or handoff docs. If you touch older artifacts and see them, redact them as part of review hygiene.

## CardForge CF-E1-S4 example

A MiniMax/M2.7 subagent implemented most sales correction work but stopped with type/test issues. The reviewer fixed the minimal remaining problems, reran validation (`typecheck`, `lint`, `test`, `prisma validate`, `build`, `git diff --check`, JSON/YAML parse), then issued `PASS WITH NOTES` and reconciled artifacts. The key learning is not the specific CardForge code; it is the orchestration boundary: M2.x can implement correction, but Alice must own final verification, review verdict, artifact reconciliation, and redaction hygiene.
