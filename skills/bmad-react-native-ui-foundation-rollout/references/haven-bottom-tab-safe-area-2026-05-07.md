# Haven bottom tab safe-area correction — 2026-05-07

## Context

During Haven Story 5.1 premium Android shell polish, the first Android screenshot looked acceptable from a styling perspective but the user noticed the bottom tab options sat at the very bottom of the Samsung screen and were hidden behind / too close to the phone's native Android navigation bar.

## Root cause

The premium pass converted the React Navigation bottom tab bar into an absolutely positioned floating shell with fixed values:

- fixed `height`
- small `marginBottom`
- fixed `paddingBottom`

That styling ignored physical-device bottom safe-area/native-navigation clearance.

## Fix pattern

Inside the component that creates the tab navigator:

```ts
import { useSafeAreaInsets } from 'react-native-safe-area-context';

function AppTabs() {
  const insets = useSafeAreaInsets();
  const bottomClearance = Math.max(insets.bottom, spacing.xxl);

  return (
    <Tab.Navigator
      screenOptions={{
        tabBarIcon: () => null,
        tabBarStyle: [
          styles.tabBar,
          {
            height: 60 + bottomClearance,
            marginBottom: bottomClearance,
            paddingBottom: Math.max(insets.bottom, spacing.md),
          },
        ],
      }}
    />
  );
}
```

Keep the base `styles.tabBar` focused on stable shell styling such as background, border radius, horizontal margins, top padding, absolute positioning, and elevation. Do not leave conflicting fixed bottom margin/padding in the base style.

## Verification pattern

Run at least:

- `npm run typecheck`
- `npm test` if present
- `npx expo install --check` if Expo app
- Android release build/install on the physical target device
- `adb` screenshot capture
- `uiautomator dump` XML capture

Parse the XML for tab labels and bounds, and visually inspect the screenshot. For Haven, the corrected run confirmed:

- labels: `Today`, `Calendar`, `Bookings`, `More`
- no placeholder glyph: `⏷` absent
- tab row bounds around `y=1263..1352` on a 720x1520 capture, leaving visible bottom clearance

## Pitfall

A screenshot filename like `today-tabbar-safe-area.png` is not enough. Inspect the actual image/XML and ensure the app, not launcher/recents, is foregrounded and the tab labels are spatially above the native navigation controls.
