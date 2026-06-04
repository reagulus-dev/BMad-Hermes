# CardForge CF-E4-S2 OAuth story selection pattern

Use this when progressing from a code-reviewed Shopify/marketplace foundation story into the next OAuth/connection story.

## State-check trigger

After CF-E4-S1-style foundation review passes with notes:

- Confirm repo is clean/synced and prior story status is `completed` / `PASS_WITH_NOTES`.
- Confirm no blockers remain; carry live API / migration / runtime gaps as notes, not blockers, if they were explicitly out of scope.
- Select the next canonical story from the plan rather than inventing a cleanup story when the prior notes naturally belong to OAuth/publishing/webhook stories.

## Story scope for OAuth connection

Create a story focused on secure connection only:

- OAuth start/callback routes.
- Shop-domain normalization and rejection of unsafe/non-Shopify values.
- Signed, expiring, owner/session-bound OAuth state.
- Shopify callback HMAC verification using canonical query params.
- Token exchange behind a mocked/testable boundary.
- Server-only token encryption/decryption using the configured token-encryption key.
- Owner-scoped connection repository/service paths.
- Dashboard states: missing config, configured-not-connected, connected non-secret status.

## Keep out of scope

Do not let OAuth story silently absorb later channel work:

- product publishing,
- Admin GraphQL product/listing calls beyond OAuth token exchange,
- webhooks/order reconciliation,
- checkout/order verification,
- live success claims without a real development store and credentials.

## Artifact sync pattern

- New story artifact: `_bmad/artifacts/stories/<ID>-shopify-oauth-connection.md`, `status: ready_for_dev`.
- `_bmad/state.json`: `workflow_status: story_created`, `active_workflow: bmad-dev-story`, `current_story: <ID>`.
- `_bmad/sprint-status.yaml`: previous story remains completed; new story inserted as `ready_for_dev` with `review_verdict: NOT_REVIEWED`.
- `CONTINUE-HERE.md`: top section must point at the new story, with prior foundation story moved to previous/completed status.
- Parse JSON/YAML and run `git diff --check`; no need to rerun full app test/build for doc-only story creation.

## Consent-guard pitfall

If a batch artifact update script is blocked by a consent guard before making changes, do not retry via a different tool or claim the story was created. Ask for explicit permission to write the BMad artifacts and commit/push, then rerun the intended update once confirmed.
