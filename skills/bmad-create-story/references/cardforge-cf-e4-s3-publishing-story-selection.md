# CardForge CF-E4-S3 publishing story selection pattern

Use when progressing CardForge from a passing Shopify OAuth connection story into the first Shopify product-publishing story.

## Trigger

- CF-E4-S2 has a fresh `PASS_WITH_NOTES` code review.
- `_bmad/state.json` and `_bmad/sprint-status.yaml` point to `bmad-state-check` / CF-E4 next workflow selection.
- Canonical planning artifacts identify CF-E4-S3 as Shopify Product Publishing.

## State-check selection

Inspect:
- `_bmad/state.json`
- `_bmad/sprint-status.yaml`
- `_bmad/artifacts/planning/epics_and_stories.md`
- `_bmad/artifacts/planning/CF-E4-shopify-store-module-plan.md`
- `CONTINUE-HERE.md`
- git status/log

Expected next story:
- `CF-E4-S3 — Shopify Product Publishing`
- Scope: publish selected available CardForge inventory to Shopify-hosted storefront products/variants, draft by default.

## Story creation boundaries

The story should be **ready_for_dev**, not implemented. Keep it bounded to:
- server-only Shopify Admin GraphQL client boundary with injectable/mocked network layer
- pure product mapper from CardForge inventory + listing input to Shopify draft product/variant payload
- owner-scoped publish service/action using the CF-E4-S2 connection/token boundary
- safe `/shopify` connected-state publish UI for selected available inventory
- listing identity/status/error persistence, additive schema changes only if needed
- focused mocked tests for mapper, owner scope, no-live-network behavior, failure persistence, and UI/action validation

Explicit out of scope:
- live Shopify API/dev-store success unless separately verified
- active/live products by default
- product image upload/generation
- webhooks/order reconciliation
- checkout/order verification
- release/founder QA readiness

## Acceptance-criteria details to include

Include ACs that prevent common future blockers:
- Admin client boundary is server-only and token-safe.
- Publish action requires authenticated owner and connected, non-disabled Shopify connection.
- Publish rejects card items not owned by current owner.
- Publish rejects archived, sold/lost/damaged, zero-quantity, or otherwise unavailable inventory.
- Listing price is user-facing GBP at the UI/action boundary and converts to CardForge integer millipence semantics; never use cost basis as listing price.
- Successful publish creates/updates a Shopify **DRAFT** product through mocked client boundary and persists owner-scoped listing identity/status.
- Shopify failures record safe `last_error` and do not mutate CardForge inventory quantity/status.
- `/shopify` renders missing-config, configured-not-connected, connected-with-publish-panel, success, and safe-error states without exposing secrets.

## Artifact synchronization

After creating `_bmad/artifacts/stories/CF-E4-S3-shopify-product-publishing.md`:
- Update `epics_and_stories.md`: mark CF-E4-S2 `review_passed_with_notes`; mark CF-E4-S3 `ready_for_dev` with mocked/no-live-claim boundary.
- Update `sprint-status.yaml`: `current_story: CF-E4-S3`; add CF-E4-S3 block with `status: ready_for_dev`, `review_verdict: pending`, `next_recommended_workflow: bmad-dev-story for CF-E4-S3`.
- Update `state.json`: `workflow_status: story_created`, `active_workflow: bmad-dev-story`, `current_story: CF-E4-S3`, `active_story_artifact` to the new story, and `next_recommended_workflows` to `bmad-dev-story for CF-E4-S3`.
- Update `CONTINUE-HERE.md`: top status points to CF-E4-S3 dev-story; keep CF-E4-S2 as previous/completed history.
- Parse JSON/YAML and run `git diff --check` before commit.

## Commit pattern

Use a focused docs commit, e.g.:

```text
docs(CF-E4-S3): create Shopify publishing story
```
