# Helix HLX-1.5 — Shared Logging/Diagnostics Foundation Example

Session pattern captured from `HLX-1.5 — Add redacted logging and basic diagnostics foundation`.

## Class of work

Shared TypeScript package foundation story with security-sensitive logging/redaction behavior and no product runtime UI yet.

## Useful implementation shape

For a foundation `@project/logging` package, keep V1 dependency-light and testable:

- structured JSON logger that emits one JSON line per event
- explicit log levels (`debug`, `info`, `warn`, `error`)
- optional correlation/context fields (`correlation_id`, `task_id`, `workflow_id`, `profile_id`, `session_id`, `worker_id`)
- injectable sink and deterministic clock for tests
- exported factory plus direct class API where docs promise one
- deep-copy `redact()` function that never mutates caller objects
- static redaction constants/patterns rather than hidden runtime magic
- bounded in-memory diagnostic channel placeholder with subscribe/unsubscribe/snapshot/clear

## Redaction test coverage to require

At minimum cover:

- nested objects and arrays
- case-insensitive sensitive keys
- token/auth header patterns (`Bearer`, `Basic`)
- cookie-like strings
- sensitive URL query parameters
- OTP/code-looking numeric values only under OTP/code-like keys
- preservation of safe operational metadata such as `product_id`, `price`, `quantity`, `stock_state`, `available`, `queue_position`, and correlation IDs
- non-mutation of input objects

## Evidence bundle

For a shared package story, static/unit/build evidence is enough only when runtime integration is explicitly out of scope:

```bash
pnpm --filter <logging-package> run typecheck
pnpm --filter <logging-package> run test
pnpm -r run typecheck
pnpm -r run test
pnpm -r run build
grep -R -I -n -i -E '(password|secret|api[_-]?key|token|credential|cookie|bearer|authorization|payment|card_number|cvv|otp|webhook|private[ _-]?key)' <logging-package-path> --include='*.ts' --include='*.md' --include='*.json' --exclude-dir=node_modules --exclude-dir=dist || true
```

Classify grep hits precisely:

- implementation constants/patterns: acceptable with note
- README policy/example text: acceptable with note
- synthetic fixtures in redaction tests: acceptable with note
- real credentials/accounts/tokens/cookies/payment data: blocker

## Review/status wording

Use `PASS WITH NOTES` when implementation and validation are sound but runtime integration is not claimed.

Explicitly state non-goals/unverified areas:

- Electron/UI diagnostic surface and IPC
- Redis/PostgreSQL/file logging sinks beyond stdout/injectable sink abstraction
- OpenTelemetry SDK integration
- worker/orchestrator runtime instrumentation
- live vendor behavior
- checkout/final-submit/3DS/SCA/OTP behavior

If the project has no `.git`, do not block solely on missing diff evidence. Record that git status/diff is unavailable and review by direct story/file inspection plus validation output.

## Delegation lesson

When MiniMax M2.7 is used for this class of story, treat wrapper failures/non-zero exits as partial-untrusted output if files were written. Read the final files, fix bounded gaps directly, rerun validation, and record the accepted state as controller-verified rather than delegate-complete.
