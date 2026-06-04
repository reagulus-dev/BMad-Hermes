# Acceptance-Criteria Evidence Mismatch Review Pattern

Use this when a story is a multi-AC cleanup/hardening sweep and the Dev Agent Record claims specific tests or files were added.

## Review stance

A passing workspace test run is not enough when an AC explicitly requires focused regression tests. Verify that the named tests/files actually exist and exercise the promised behavior.

## Checklist

- Cross-check the Dev Agent Record against the filesystem:
  - If it says `foo.test.ts` was added, confirm the file exists.
  - If it says specific test cases were added, search/read the test file for those cases or equivalent assertions.
- For each AC with required tests, classify separately:
  - implementation code present,
  - focused test evidence present,
  - validation command passed.
- If implementation appears correct but required focused tests are absent or misreported, use `BLOCKED` when the story AC made those tests part of completion.
- Record the blocker as an evidence/completion-contract problem, not necessarily a code-correctness failure.
- Required correction should be narrow: add the missing tests/evidence, reconcile the Dev Agent Record, rerun focused/workspace validation, then request fresh review.

## Common examples

- Service/IPC boundary clamp added, but no service/IPC test proves untrusted renderer input is normalized before DB calls.
- UUID/input validation added, but no test proves invalid/empty values reject before executor invocation.
- Sanitization helper exists, but failure-path tests only assert a generic throw and do not assert secret-bearing output is redacted.

## Pitfall

Do not let the existence of broad passing tests or a clean typecheck mask a mismatch between AC wording and the evidence contract. Multi-AC tech-debt stories often fail on missing evidence even when most code is reasonable.
