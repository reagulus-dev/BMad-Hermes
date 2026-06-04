# Haven premium Android shell polish — 2026-05-07

## Class of work

Bounded mobile visual-polish / premium-shell story for an Expo React Native app, using an existing app's design-system logic as inspiration without copying product personality.

## What worked

- Keep the slice bounded: shared tokens/components, app shell chrome, Today/demo-critical screen polish, and one secondary list/form surface.
- Prefer dependency-light polish first: muted palette, tighter spacing, larger radii, Android-safe elevation, status/action pills, better cards and hierarchy.
- Run the full cheap validation stack after style changes:
  - `npm run typecheck`
  - `npm test`
  - `npx expo install --check`
  - `npx expo export --platform web --output-dir <tmp>`
  - Android `./gradlew assembleRelease`
  - Android `adb install -r <apk>`
- Use Android screenshot + XML capture as evidence, not screenshots alone. XML is the fastest way to catch wrong-screen evidence and navigation chrome regressions.

## Review finding that mattered

The first focused review blocked signoff because React Navigation bottom tabs rendered default placeholder `⏷` glyphs in the premium shell. TypeScript/export/build all passed, but Android XML showed:

- `content-desc="⏷, Today"`
- `content-desc="⏷, Calendar"`
- `content-desc="⏷, Bookings"`
- `content-desc="⏷, More"`

Fix used in Haven:

```tsx
screenOptions={{
  tabBarIcon: () => null,
  tabBarLabelStyle: styles.tabBarLabel,
  tabBarStyle: styles.tabBar,
}}
```

`tabBarShowIcon: false` was attempted first but was not a valid option for the installed bottom-tabs typings, so typecheck failed. `tabBarIcon: () => null` typechecked and removed the placeholder glyphs.

## Appium evidence pitfall

The Appium screenshot runner produced `02-bookings-premium-polish.png`, but the XML still contained `today-screen`, `OPERATIONS COCKPIT`, and Today rows. The correct response was to mark Bookings Android visual evidence as **not proven**, while retaining source/typecheck/export/build/install coverage for Bookings.

Do not infer screen coverage from:

- screenshot filenames
- runner step names
- a successful Appium session
- a visible tab label somewhere in the tree

Do verify:

- unique screen root testID, such as `bookings-screen`
- unique hero/header copy, such as `RESERVATIONS LEDGER`
- selected tab/navigation state where accessible
- absence of auth/launcher/error screen markers

## Launcher/recents pitfall

A runner variant that pressed Back during startup captured the Samsung launcher/recents instead of Haven. Before saving visual evidence, force-stop/start the package and confirm XML package + screen markers:

```bash
adb -s <device> shell am force-stop app.appsfoundry.haven
adb -s <device> shell am start -n app.appsfoundry.haven/app.appsfoundry.haven.MainActivity
adb -s <device> shell uiautomator dump /sdcard/current.xml
adb -s <device> shell cat /sdcard/current.xml | grep -E 'today-screen|bookings-screen|OPERATIONS COCKPIT|RESERVATIONS LEDGER'
```

## Honest status wording

Use:

- `complete_with_notes` when source/build coverage passes but one visual surface lacks valid screenshot evidence
- `PASS WITH NOTES` when review blockers were fixed but runtime evidence remains partial

Avoid:

- `founder-review ready`
- `Bookings visually verified`
- `Android UI verified` for all touched screens when only Today captured correctly

## Suggested next step after this pattern

If the product needs founder-review readiness, run a dedicated visual QA/founder review pass with manually inspected screenshots for each demo-critical screen, then separately run iOS launch/runtime smoke.
