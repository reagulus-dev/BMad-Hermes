# MiniMax M2.7 Subagent Exit Early Pitfall

## Pattern

When delegating `bmad-dev-story` (or similar implementation) to MiniMax M2.7 via Hermes CLI subagent, the subagent often exits with wrapper status 255 before completing a full verified handoff. All implementation files may be written to disk, but the subagent's final verification step (rerunning validation, recording evidence) may be skipped.

**Evidence:**
- HLX-1.2: MiniMax produced all 8 implementation files, exited status 255. Controller inspected, found `Object.freeze()` + `as const` redundancy on `VISUAL_TOKENS`, corrected, reran all validation.
- HLX-1.5: MiniMax partially implemented `@helix/logging`, exited status 255. Controller inspected, corrected tests/docs, reran validation.
- CardForge CF-E1-S5: MiniMax produced useful GBP-expense correction edits and partial BMad artifacts, then exited status 255. Controller accepted only the verified repo state, moved the GBP conversion helper into production money utilities, replaced self-contained/mock-only tests with tests that exercise production server actions and repository boundaries, reran validation, and reconciled story/state/sprint/continuation artifacts.

## Controller Workflow After Subagent Exit

1. **Don't assume the story is incomplete** — check `apps/*`, `packages/*`, `src/*`, tests, and BMad artifacts for actual writes.
2. **Read implementation files** directly from disk (not relying on subagent output summary).
3. **Run validation** (`typecheck/test/build`) on the actual files.
4. **Apply corrections** if the subagent's output has issues (syntax errors, stale imports, missing test updates, weak/mock-only tests, helper logic hidden inside actions instead of reusable production utilities, etc.).
5. **Tighten tests to production boundaries**: for story blockers, prefer tests that call exported production helpers/actions/repos over tests that merely duplicate the intended logic in the test file.
6. **Rerun validation** and record evidence.
7. **Update CONTINUE-HERE.md and BMad artifacts** with both subagent and controller actions; if controller changes validation counts or scope, overwrite stale subagent evidence rather than preserving contradictory numbers.

## Common Issues Found

- Redundant type annotations (e.g., `Object.freeze({...} as const)` — the `as const` is unnecessary).
- Missing test updates after implementation changes.
- Stale imports from renamed modules.
- Documentation examples referencing non-existent APIs.

## Key Rule

A subagent exit with non-zero status ≠ implementation failure. Always inspect actual files on disk before routing back to correction work.