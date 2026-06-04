# TypeScript Contract-Only Story Review

Use when a BMad story only defines shared TypeScript contracts: event envelopes, channels, lifecycle states, guardrails, config shapes, payload interfaces, or exported constants.

## Checklist

- **Current-scope values:** literal unions and constants match the active product/version. Do not expose deferred roadmap features as active contract surface unless the story explicitly requires forward-compatible values.
- **Required-field tests:** tests should assert mandatory envelope/config/result fields by name, not merely instantiate a type or check imports.
- **Representative values:** tests should include the important allowed values: event channels, lifecycle states, guardrail decisions, config channel types, and redaction placeholders.
- **Contract-only boundary:** no runtime clients, config loaders, DB/Redis/browser dependencies, Electron UI, Playwright automation, checkout/final-submit behavior, or live vendor logic.
- **Redaction safety:** examples must use opaque references or redacted strings for webhook URLs, tokens, passwords, cookies, payment data, profile paths, and OTP values.
- **Evidence honesty:** typecheck/test/build can justify a contract-review pass, but not runtime readiness. Explicitly list runtime areas not verified.

## Example correction pattern

If a contract includes deferred values, narrow it before passing review.

Example: V1 notifications are desktop + Discord, while Slack/email are later roadmap support.

```ts
// Too broad for V1 contract surface
export type NotificationChannel = 'desktop' | 'discord' | 'slack' | 'email';

// Correct for V1 if Slack/email are explicitly deferred
export type NotificationChannel = 'desktop' | 'discord';
```

Add a regression test that encodes the product boundary, for example asserting the accepted V1 channels are exactly `desktop` and `discord`.

## Non-git worktree fallback

Some early project directories may not yet be initialized as git repositories. In that case:
- record that git status/diff evidence is unavailable;
- inspect the target files directly;
- compare against the story scope and source artifacts;
- rerun validation commands independently;
- do not claim diff-based provenance.
