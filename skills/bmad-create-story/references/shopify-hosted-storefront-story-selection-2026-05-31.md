# Shopify-hosted storefront story selection pattern (CardForge, 2026-05-31)

Use when a new external-channel/storefront feature is being turned from a broad technical plan into the first BMad implementation story.

## Durable lesson

Before creating the first story, ground the channel architecture in a real reference implementation if the user asks “how does this work?” or points to a competitor/reference site. For Shopify, inspecting NeoSatoshi showed the target was a Shopify-hosted storefront, not a custom CardForge storefront with Shopify payments bolted on.

## Pattern

1. Update the technical plan before story creation when discovery changes or clarifies architecture.
   - Capture the reference evidence concisely.
   - State the chosen model explicitly: private app/admin system vs public hosted storefront.
   - Convert generic rollout labels (Story A/B/C) into the project’s current epic/story IDs.

2. Reconcile epic numbering and stale deferred labels.
   - If a prior “CF-E3” has since been used for another completed epic, do not overload it.
   - Create the next clean epic (e.g. CF-E4) and update `epics_and_stories.md`, `sprint-status.yaml`, `_bmad/state.json`, and `CONTINUE-HERE.md` together.

3. Make the first story intentionally safe.
   - Foundation story only: enum/config/schema/dashboard shell.
   - Explicitly out of scope: OAuth, live API calls, product publishing, webhooks, checkout/order verification.
   - State that live external behavior remains unverified until the relevant later story.

4. Validate the artifact set before handoff.
   - Parse story frontmatter.
   - Parse `_bmad/state.json` and `_bmad/sprint-status.yaml`.
   - Confirm both point to the same current story.
   - Run diff hygiene (`git diff --check`) before reporting completion.

## Example outcome

- Plan: `_bmad/artifacts/planning/CF-E4-shopify-store-module-plan.md`
- Story: `_bmad/artifacts/stories/CF-E4-S1-shopify-foundation.md`
- State/sprint current story: `CF-E4-S1`
- Next workflow: `bmad-dev-story for CF-E4-S1`
