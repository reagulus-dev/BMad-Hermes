# Electron Route/Proxy Configuration Review Blockers (HLX-3.5, 2026-05-18)

Use this reference when reviewing Electron route/proxy/network configuration stories that add DB-backed route groups, health metadata, and operator-facing route UI.

## Review lesson

A `story_completed` state claim is not enough to advance if the story artifact, sprint status, tests, and acceptance criteria disagree. Treat the implementation as reviewable but not complete, run the review gate, and reconcile BMad state to the verdict.

## Concrete blocker patterns

1. Workspace renderer tests fail after route UI changes
   - If the story touches the static renderer entry (for example `nav-init.js`), failing renderer tests cannot be casually classified as unrelated.
   - Require either a clean workspace test run or a tight proof that failures are unrelated plus focused passing tests for the new route UI.

2. Missing focused route UI reachability tests
   - For DB-backed route configuration screens, tests should exercise the rendered route through the real preload API shape:
     - `helixRoutes.list()` renders rows and empty/error states.
     - selecting a row opens detail.
     - create/edit/delete call the expected preload methods with object payloads.
     - health check calls `runHealthCheck(id)` and refreshes/renders updated metadata.
   - Repository and service tests alone do not satisfy operator-facing acceptance criteria.

3. Redaction helper exists but is not wired
   - A standalone `redactRouteConfig()` helper and unit tests are insufficient if create/update persistence still accepts raw parsed proxy config.
   - Review the full path: renderer prompt/form → preload IPC → service → repository → DB row → detail display.
   - Block if plaintext proxy credentials/tokens/API keys can be persisted or displayed, or if the story requires redacted display but detail omits config entirely.

4. Monitor-vs-checkout continuity risk copy missing
   - Route models often encode `role: monitor | checkout | shared`.
   - If acceptance criteria require route/profile/session continuity risk labeling, showing only the raw role is not enough.
   - Require explicit operator-facing copy warning that differing monitor and checkout routes can affect session continuity/risk.

5. `ipcMain.handle` cleanup uses listener APIs
   - For invoke handlers registered with `ipcMain.handle(...)`, cleanup/re-registration should use `ipcMain.removeHandler(channel)` or be explicitly single-registration-only.
   - `ipcMain.removeListener(...)` does not remove invoke handlers and is a review footgun.

## BMad reconciliation pattern

When review blocks a story whose state claims completion:
- Append the review findings to the story artifact.
- Set `_bmad/state.json` to `workflow_status: review_blocked` and remove the story from `completed_stories` if present.
- Update sprint status to `review_blocked` with `review_verdict: BLOCKED`.
- Route next workflow to a focused same-story `bmad-dev-story` correction followed by fresh review.
