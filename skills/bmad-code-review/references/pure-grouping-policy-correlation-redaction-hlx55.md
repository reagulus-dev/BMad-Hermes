# Pure grouping policy correlation redaction pitfall (HLX-5.5)

Session pattern: a post-BLOCKED correction claimed AC6 secret-safety coverage for grouping output, but the review found one echoed field still unsafe.

## What happened

- `GroupedLine.product_name` was redacted.
- skipped-reason messages were redacted.
- `GroupedLine.correlation_id` was still copied directly from `candidate.event.correlation_id`.
- The test named `redacts/omits secret-like correlation_id from output lines` used a normal value (`worker:worker-a:task-001`) instead of injecting a secret-like value.
- Result: the static secret list was absent from output, but the test did not prove correlation-id redaction.

## Review rule

When ACs require non-sensitive grouping state/logs, inspect every output-bearing field copied from events/candidates/owner context, especially fields that sound operationally safe but may carry upstream data:

- `product_name`
- `correlation_id`
- event references / source references
- owner IDs in human-readable messages
- skipped reason messages
- log payload messages

A test is insufficient if it only checks that a hard-coded secret list is absent from normal fixtures. It must inject representative secret-like values directly into each field the policy echoes, then assert the raw values are absent from the full serialized result/log.

## Passing correction shape

- Redact, omit, or reject secret-like `event.correlation_id` before assigning it to output.
- Add at least one focused regression test that sets `event.correlation_id` to a representative secret-like value (for example Bearer/JWT/API key/webhook/session/payment token) and asserts `JSON.stringify(result)` does not contain the raw value.
- Keep normal safe correlation references if product requirements need them, but distinguish safe refs from raw upstream strings.
