# Haven floating tab scroll-content overlap — 2026-05-08

## Context

After a prior Haven fix moved the premium floating bottom tabs above Android native navigation using `useSafeAreaInsets()`, a follow-up UI audit found a second layout class: scroll content still rendered underneath the floating tab shell.

Device/runtime context:
- Project: `/home/reagulus/projects/Haven`
- Device: Samsung Galaxy S10 `RF8M40ZMDHY`, Android 12
- App package: `app.appsfoundry.haven`
- Capture size: 720x1520
- Prior safe-area tab labels were above native nav, but content clearance remained inconsistent.

## Evidence pattern

The floating tab buttons occupied roughly:

- Tab button bounds: `y=1263..1352`
- Tab label bounds: `y=1320..1350`

Bottom-of-scroll captures showed content inside the same y-range:

- Calendar bottom state:
  - `No availability blocks`: `y=1307..1344`
  - overlapped the floating tab area.
- Bookings bottom state:
  - `ADD BOOKING`: `y=1279..1312`
  - overlapped the floating tab area.

This proves that a screenshot of the top/default screen state is not enough; verify bottom-of-scroll states when tab bars are absolute/floating.

## Root cause pattern

- React Navigation tab bar is `position: 'absolute'` and has runtime-derived height/margin/padding.
- Individual tab screens own their own `ScrollView` `contentContainerStyle.paddingBottom`.
- Some screens used `paddingBottom: 24`; others used guessed larger values such as `paddingBottom: 92`.
- The scroll content padding was not derived from the same tab-shell geometry as the tab bar.

## Reusable fix direction

Do not patch each tab with ad hoc padding. Introduce or extend a shared tab-screen scroll primitive so all tab bodies receive consistent bottom clearance.

Good shape:

- Centralize tab-shell geometry in tokens or shell helpers.
- Derive a `tabBarClearance` that includes the floating tab height, bottom margin/safe-area clearance, and a small breathing spacer.
- Apply that clearance to all tab `ScrollView`/FlatList content containers.
- Keep the actual tab bar placement and content inset contract in one place where possible.

## Session implementation outcome

Final Haven correction used this shape:
- `src/features/shared/Screen.tsx`: added `TabScrollView` using `useSafeAreaInsets()`.
- `src/features/shared/tokens.ts`: added shared floating-tab base height/gap tokens.
- `App.tsx`: tab bar uses the same floating-tab base-height token.
- Today, Calendar, Bookings, and More replaced fixed `ScrollView` bottom padding with `TabScrollView`.

Final Android XML verification on Samsung Galaxy S10 showed positive bottom-scroll clearance:
- Today: 74px
- Calendar: 74px
- Bookings: 90px
- More: 90px

One session-specific tool pitfall: local PNG paths were valid on disk, but the vision analyzer rejected them. Do not block the gate on that when XML bounds and screenshot files are captured; record the limitation and keep the screenshot artifacts for human review.

## Verification checklist

For floating tab safe-area/layout fixes, run:

1. Android physical-device screenshot/XML at initial tab state.
2. Android physical-device screenshot/XML at bottom-of-scroll state for each tab with scrollable content.
3. Parse tab button bounds and lowest visible content bounds.
4. Confirm content CTAs/text do not occupy the tab-button y-range.
5. If claiming cross-platform readiness, capture iOS simulator/device evidence too; static source review is not enough for iOS home-indicator behavior.

## Pitfall

A successful native-navigation clearance fix can create a false sense of completion. Treat floating tab layout as two contracts: tab vs native nav, and content vs tab. Both must pass before calling the shell corrected.
