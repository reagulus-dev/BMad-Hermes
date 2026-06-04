---
name: bmad-qa-gate
description: Strengthen QA/release gating for BMad. Distinguishes test generation from true founder-review readiness and requires runtime evidence for usability-sensitive app flows.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, qa, release, gating, validation, founder-review]
    related_skills: [bmad-code-review, bmad-evidence-reporting, bmad-artifact-policy, bmad-dev-story]
---

# BMad QA Gate

## Goal

Prevent false QA passes and false `ready for founder review` claims.

## Canonical Naming Rule

For BMad-managed live state, use `snake_case` consistently.

Preferred field names include:
- `workflow_status`
- `last_review_summary`
- `last_evidence_path`
- `last_artifacts`
- `next_recommended_workflows`
- `updated_at`

Do not continue schema drift by introducing new gate-related state references in camelCase.

## Important Distinction

Test automation generation is NOT the same as QA signoff.
Passing tests is NOT the same as app usability.
Code review is NOT the same as runtime validation.

## Use When

Use before saying any of the following:
- ready for QA
- QA passed
- ready for founder review
- founder review ready
- ready for release
- app is done

## Required Evidence Classes

For Expo/React Native Android release runtime QA, also consult `references/android-release-runtime-qa.md` for the clean release-APK + UIAutomator screenshot/XML + logcat evidence pattern.

For Electron/desktop apps on headless Linux, consult `references/electron-xvfb-runtime-qa.md` for the Xvfb virtual display + runner script + computed-styles verification pattern.

For Next.js/Supabase web apps that have passed code review but still need first founder/manual runtime smoke, consult `references/nextjs-lan-runtime-qa-cardforge.md` for the local/LAN production-server pattern (`next build`, bind `next start` to `0.0.0.0`, verify loopback + LAN URL, keep PID/logs ignored, and avoid premature Vercel deployment when local QA is sufficient).

For Electron flows backed by local database rows, also consult `references/electron-db-backed-ui-qa.md` for the raw-DB vs repository-helper vs renderer diagnosis pattern and the `psql --tuples-only` delimiter/parsing pitfall.

For Electron DB-backed health/status metadata QA, also consult `references/electron-db-health-timestamp-runtime-qa-2026-05-18.md` for the ISO timestamp `::timestamptz` casting pitfall and the bounded same-gate correction pattern when runtime QA finds a small in-scope blocker.

### 1. Implementation evidence
- target story or fix identified
- changed files known
- build, test, or static validation results recorded

### 2. Review evidence
- code review performed
- blocking findings resolved or explicitly listed

### 3. Runtime evidence
For usability-sensitive flows, require real runtime evidence such as:
- manual testing on the actual build or device
- end-to-end execution on the actual app path
- screenshot, video, or log evidence where useful

For Expo/React Native web parity gates, a passing `expo export --platform web` is only build evidence. Browser form verification needs an actual web runtime session that exercises inputs, buttons, confirmations, and visible success/error states. React Native Web can differ from native for dialogs and touchable text nesting, so treat web form paths as their own runtime surface.

Usability-sensitive flows include:
- auth
- onboarding
- navigation
- payments or subscriptions
- forms and save flows
- notifications
- household or shared-state flows
- scanner or camera flows
- anything the founder will directly judge as core app usability

## Founder Review Gate

Do NOT say founder-review ready unless all are true:
- the scoped change or story is identified
- code review is complete or explicitly waived with reason
- runtime verification happened on the relevant app surface or build
- known bugs affecting the scoped area are listed
- remaining unverified areas are explicitly listed

## Verdict Labels

Use one of:
- test-generated only
- code-reviewed, runtime-unverified
- runtime-verified for scoped flow
- founder-review ready for scoped flow
- blocked

If runtime evidence is absent, the strongest allowed verdict for usability-sensitive work is:
- `code-reviewed, runtime-unverified`

## Required Output Block

Always include:
- Change target
- Validation command(s)
- Runtime verification
- Result
- Unverified
- Gate verdict

## Artifact Routing Rule

For story-linked work, always append findings to the `## QA Findings` section of the story artifact.
Do not create a separate QA file for story-scoped work.
Create a standalone QA artifact under `_bmad/artifacts/qa/` only when findings are cross-story, release-wide, or too large to fit in the story thread.

When a QA pass closes a previously listed gap, reconcile old continuation/status text before final reporting:
- search story files, `CONTINUE-HERE.md`, current-plan/status docs, and `_bmad/state.json` for stale `pending` / `unverified` phrases tied to the closed gap
- update old sections as `superseded by later QA findings` instead of erasing useful history
- keep the remaining unverified surfaces explicit, especially iOS/browser/cross-platform founder-review gaps

See `references/haven-story-2-2-runtime-browser-qa-2026-05-07.md` for a concrete Android + browser QA gate, React Native Web `Alert.alert` correction, and stale-status reconciliation pattern.

## State Handling

After applying the QA gate, ensure `_bmad/state.json` reflects reality:
- `workflow_status` should not be upgraded beyond what the evidence truly supports
- `last_review_summary` and `last_evidence_path` should already exist or their absence should be called out explicitly as a gap
- `last_artifacts` should include the most relevant story, QA, review, or evidence anchors
- `next_recommended_workflows` should be explicit
- `updated_at` should be refreshed

Do not set a completion-like state based on test generation alone.

## Manual QA Feedback Loop

When manual testing finds bugs after a nominal pass:
1. treat that as evidence the gate was too weak
2. route the issue into `bmad-correct-course`, `bmad-dev-story`, or `bmad-code-review` as appropriate
3. append findings to the relevant story or QA thread
4. patch the relevant Alice skill if the process gap is reusable

## QA-Found Blocker Correction Loop

When a runtime QA gate itself finds a small, clearly in-scope blocker:
1. record the initial failing runtime evidence instead of hiding it
2. investigate root cause before fixing; do not guess from symptoms
3. apply a bounded same-story correction only if the cause and scope are clear
4. add or update a focused regression test for the runtime failure
5. re-run the failed runtime path and the broader validation needed for confidence
6. append both the initial blocker and corrected pass to the story `## QA Findings` section
7. reconcile `_bmad/state.json`, `_bmad/sprint-status.yaml`, `CONTINUE-HERE.md`, and stale `runtime-unverified` / `QA pending` text

If the blocker is broad, architectural, or outside the story scope, stop the gate as `blocked` and route to `bmad-correct-course` or `bmad-dev-story` instead.

## YOLO Mode Policy

Autonomous or YOLO implementation is allowed.
Autonomous completion claims are not allowed to outrun evidence.
The stronger the autonomy, the stricter the gate must be.

## Completion Standard

A good QA gate prevents unusable software from being presented as ready.
