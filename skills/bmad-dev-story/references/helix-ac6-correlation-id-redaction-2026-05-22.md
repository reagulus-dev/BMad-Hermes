# HLX-5.5: AC6 correlation_id redaction pattern (2026-05-22)

Context:
- HLX-5.5 fresh bmad-code-review was BLOCKED:
  - GroupedLine.correlation_id was directly assigned from candidate.event.correlation_id.
  - Existing “secret-like correlation_id” test used a normal worker reference (worker:worker-a:task-001), not a real secret-like value.
- A malformed/adversarial event could leak secrets via result.lines[*].correlation_id.

Correction:
- In cartGrouping.ts:
  - correlation_id: redact(candidate.event.correlation_id)
- In cartGrouping.test.ts:
  - New regression test:
    - const secretCorrelationId = 'Bearer eyJhbG...cret';
    - Assert:
      - JSON.stringify(result) does not contain 'Bearer eyJhbG...cret'.
      - result.lines[0].correlation_id !== secretCorrelationId.

Review expectations (use this as a template for similar AC6/security-output gaps):
- Any field that:
  - Comes directly from external events,
  - Is echoed into output lines, decision logs, or operator-visible structures
  must:
  - Be treated as opaque.
  - Be redacted via the same redact(value) helper used for other secret-like fields.
- A test that “normal fixtures don’t contain a static secret list” is NOT sufficient.
- A correct test:
  - Injects a representative secret-like value directly into the input field.
  - Proves it is absent from the full JSON-stringified output.
  - Proves the specific field is not set to the raw secret.

Outcome:
- HLX-5.5 AC6 resolved.
- Fresh bmad-code-review PASS WITH NOTES at HEAD 8158849.
