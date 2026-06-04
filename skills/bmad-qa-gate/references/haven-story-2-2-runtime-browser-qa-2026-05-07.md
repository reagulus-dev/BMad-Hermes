# Haven Story 2.2 Runtime + Browser QA Gate — 2026-05-07

Reusable lessons from a BMad QA gate that covered Story 2.2 Rooms & Units edit/archive plus carried browser form flows before proceeding to Epic 3 calendar work.

## Scope verified

- Android physical device runtime: fresh auth, setup establishment, room create, inline room edit/save, archive confirmation, archived row removed from active list.
- Browser interactive forms: create account, setup establishment, room create, room edit, room archive, booking create, booking conflict-error display.

## Key correction discovered

React Native `Alert.alert(...)` was reliable for native Android but did not provide a usable archive confirmation path in the web export. For React Native Web destructive confirmations, branch explicitly:

```ts
import { Alert, Platform } from 'react-native';

function confirmArchive(room: RoomUnit) {
  const message = `${room.display_name} will stop appearing as bookable inventory but remains attached to history.`;

  if (Platform.OS === 'web') {
    if (globalThis.confirm(`Archive Room & Unit?\n\n${message}`)) {
      archive(room);
    }
    return;
  }

  Alert.alert('Archive Room & Unit?', message, [
    { text: 'Cancel', style: 'cancel' },
    { text: 'Archive', style: 'destructive', onPress: () => archive(room) },
  ]);
}
```

Rebuild both web export and release APK after this kind of platform branch because the same source affects both bundles.

## Browser QA harness pattern

- Export web build after final source correction: `npx expo export --platform web --output-dir /tmp/<export>`.
- Serve export locally with a simple static server.
- Use headless Chromium/Puppeteer if Browser tool navigation is insufficient for rich RN Web interactions.
- Capture per-step screenshots + HTML and a redacted `summary.json` under `_bmad/artifacts/evidence/browser-form-qa-<run_id>/`.
- Assert visible outcome text rather than only network status.
- Treat expected server/RPC rejections (for example booking overlap HTTP 400) as non-blockers only when the UI-visible error assertion passes and the summary labels the console error as expected telemetry.

## Android Appium quirks observed

- Native Android alert destructive button text may surface uppercase (`ARCHIVE`) or as `android:id/button1`; use fallback selectors.
- Click the clickable parent/container when React Native visible text is nested inside a touchable.
- Do not wait for row text to disappear globally if historical sections may still contain the archived room name; assert the active-list empty/removed state instead.

## Documentation reconciliation pattern

After a QA gate closes a previous pending gap, search for stale continuation/status phrases before finalizing, for example:

```bash
rg "browser interactive.*pending|edit/archive.*pending|runtime.*unverified" \
  CONTINUE-HERE.md docs/foundry _bmad/artifacts/stories
```

Patch old sections as “superseded by later QA findings” rather than deleting history. Update `_bmad/state.json` with `snake_case` fields, evidence paths, next workflows, and remaining gaps.

## Evidence bundle shape used

- Android: `_bmad/artifacts/evidence/android-ui-qa-story-2-2-20260507-051633/summary.json` plus screenshots/XML.
- Browser: `_bmad/artifacts/evidence/browser-form-qa-20260507051510/summary.json` plus screenshots/HTML.
- Story anchors updated instead of creating standalone QA docs:
  - `_bmad/artifacts/stories/2-2-rooms-units-edit-archive.md`
  - `_bmad/artifacts/stories/3-1-add-booking-flow.md`
  - `_bmad/artifacts/stories/3-2-server-side-overlap-prevention.md`

## Gate wording

Safe verdict: `runtime-verified for scoped Android Story 2.2 flow and browser form flows; not full cross-platform founder-review ready`.

Remaining gap in this case: iOS runtime launch.
