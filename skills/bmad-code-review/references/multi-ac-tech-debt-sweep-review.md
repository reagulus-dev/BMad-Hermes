# Multi-AC Tech-Debt Sweep Review Pattern

Use this when a single story bundles many small tech-debt fixes across multiple packages (e.g., 10+ ACs).

## Goals

- Ensure each AC is actually addressed.
- Prevent “I did something roughly related” from passing as done.
- Keep the review concise but explicit.

## Checklist

For each AC:

- [ ] Identify touched files:
  - Main implementation file(s).
  - Test files.
  - Any shared constants or docs.
- [ ] Check:
  - AC wording vs implementation: is it a real fix or just a comment?
  - No new boundary violations:
    - Electron: preload/renderer separation, IPC-only access.
    - DB: canonical public interface (e.g., DbProfileStore) respected.
  - Tests:
    - If AC requires test coverage, is there a focused test?
    - If AC is documentation-only, is the note explicit and durable?

Verdict rules:

- PASS:
  - All ACs substantially implemented.
  - No boundary violations.
  - No missing required tests.
- PASS WITH NOTES:
  - No blockers.
  - Some ACs have minor gaps or residual issues (e.g., HTML misuse in one file, placeholder UX, wording drift).
  - All gaps are explicitly listed and non-blocking.
- BLOCKED:
  - One or more ACs:
    - Not implemented,
    - Implemented incorrectly,
    - Or introduce a clear boundary/security issue.

## Output Structure

In the story artifact under `## Review Findings`:

- Verdict: PASS / PASS WITH NOTES / BLOCKED
- Per-AC assessment:
  - AC1: PASS (brief)
  - AC2: PASS (with note)
  - ...
- Evidence inspected:
  - List key files and artifacts.
- Non-blocking findings:
  - Short, concrete, file-level notes.
- Required next action:
  - Accept, follow-up, or route back.
