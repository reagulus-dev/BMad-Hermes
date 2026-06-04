---
name: bmad-react-native-ui-foundation-rollout
description: Roll out a safe-area/keyboard/modal UI foundation in a brownfield React Native / Expo app before visual redesign work.
version: 1.0.0
author: Alice
license: MIT
metadata:
  hermes:
    tags: [bmad, react-native, expo, ui-foundation, safe-area, keyboard, modal]
    related_skills: [bmad-create-ux-design, writing-plans, test-driven-development, systematic-debugging]
---

# BMad React Native UI Foundation Rollout

## When to Use

Use when a brownfield React Native / Expo app has UI complaints like:
- keyboard hiding fields or CTA bars
- headers/tab bars colliding with notches or home indicators
- too many bespoke modal/sheet implementations
- inconsistent spacing and shell structure across screens
- a prior visual refresh failed because layout fundamentals were unstable

## Core Finding

If the app is structurally unstable, do NOT start with decorative redesign.

Change course toward foundation-first work:
1. tokens
2. screen/layout primitives
3. overlay primitives
4. shell wiring
5. highest-risk screen migration
6. only then visual polish

## Recommended Phase 1 Dependency Strategy

Default low-risk path first:
- reuse `react-native-safe-area-context` if already installed
- reuse native `Modal`, `KeyboardAvoidingView`, `ScrollView`, `Animated`
- defer `expo-blur`
- defer `@gorhom/bottom-sheet`
- defer keyboard-controller style deps unless native keyboard behavior still fails after scaffold rollout

Reason: dependency churn makes brownfield UI rescue harder to reason about.

## Canonical Phase 1 Primitives

Create a minimal shared UI layer such as:
- `AppScreen`
- `AppHeader`
- `AppScrollView`
- `AppBottomActionBar`
- `AppFormScreen`
- `AppDialog`
- `AppSheet`
- `AppFullscreenModal`
- token file for spacing/radius/layout/shadow

## Execution Order

Use this rollout order:
1. tokens + theme semantics
2. root shell and tabs safe-area wiring
3. layout primitives
4. overlay primitives
5. migrate duplicated form flows first
6. migrate shared picker/sheet components
7. migrate fragmented feature screens (settings, household, review flows)
8. run targeted regression checks
9. update continuation docs before claiming progress

## Testing Lessons Learned

### Safe-area testing
For Jest in React Native / Expo, mock `react-native-safe-area-context` in test setup if provider/view rendering is noisy or unsupported.

Important implementation detail: in Jest setup files, prefer `React.createElement(...)` over JSX when writing inline mock components if the setup file/parser path is sensitive. A JSX-based mock in `jest.setup.after.ts` can fail with confusing parser errors like `Unterminated regular expression` depending on the transform path.

### Floating bottom tabs and native navigation bars
For React Navigation bottom tabs styled as floating premium chrome, do not use a fixed `marginBottom`/`height` and assume it clears Android's native navigation bar. Read `useSafeAreaInsets()` inside the tab navigator component and derive clearance from the runtime inset, for example:

```ts
const insets = useSafeAreaInsets();
const bottomClearance = Math.max(insets.bottom, spacing.xxl);

screenOptions={{
  tabBarStyle: [
    styles.tabBar,
    {
      height: 60 + bottomClearance,
      marginBottom: bottomClearance,
      paddingBottom: Math.max(insets.bottom, spacing.md),
    },
  ],
}}
```

Verification for this class of fix should include a physical-device screenshot plus UI XML/hierarchy parsing. Confirm tab labels/buttons are above the native navigation area rather than trusting the simulator, filename, or source diff alone. If the user reports the bar is hidden behind the phone nav controls, treat it as a safe-area regression and adjust the shell before continuing visual polish.

### Floating tabs and scroll-content clearance
A bottom-tab safe-area fix is incomplete if the tab chrome is above the native navigation bar but scroll content can still render underneath the floating tab bar.

For absolute/floating tab bars, verify both sides of the contract:
1. **Chrome placement:** tab buttons/labels clear the native navigation area or iOS home indicator.
2. **Content clearance:** every tab screen's `ScrollView`/list bottom inset clears the floating tab shell at top and bottom scroll positions.

Avoid fixed per-screen values such as `paddingBottom: 24` or guessed values like `paddingBottom: 92` when the tab bar height/margin are runtime-derived. Instead, centralize the clearance in a shared tab-screen scroll primitive or pass a computed `tabBarClearance` from the shell/tokens so all tab content uses the same bottom spacer.

Runtime verification should capture bottom-of-scroll screenshots/XML, not just the initial screen. In UI XML, compare the tab button bounds with the lowest visible content bounds; if content text/CTAs occupy the same y-range as tab buttons, the layout still overlaps even if the native nav bar is clear.

Reusable script: `scripts/android_floating_tab_clearance_verify.py` can capture top/bottom screenshots/XML for a configurable tab set and fail if any screen's bottom content overlaps the floating tab bounds. Configure with `APP_PACKAGE`, `ANDROID_UDID`, `OUTPUT_DIR`, and `TAB_SPEC='key:x:Label,...'`.

### Overlay testing
For shared overlay primitives built on native `Modal`, direct render tests may be flaky or fail host-component detection depending on the library/version mix.

If that happens, switch to source-contract tests for the primitive layer instead of wasting time fighting the renderer.

This is especially useful when both of these appear together:
- native `Modal` host-component detection failures in React Native Testing Library
- async `ThemeProvider` hydration / `act(...)` noise from storage-backed theme bootstrapping

Good source-contract assertions include:
- required primitive import exists
- required testIDs exist
- required wrapper types exist (`Modal`, `KeyboardAvoidingView`, `useSafeAreaInsets`)
- migrated screens use the new scaffold (`AppFormScreen`, `AppScreen`, `AppHeader`, etc.)
- banned hardcoded layout hacks are absent (`paddingTop: 60`, fixed tab-bar heights, etc.)
- old bespoke modal markers are absent when standardization is the goal (`<Modal`, local keyboard-offset hacks, etc.)

Use runtime/device checks later for behavioral confirmation.

### TypeScript pitfall
If the repo uses `exactOptionalPropertyTypes: true`, shared primitive props often need explicit `| undefined` on optional props when you pass through maybe-undefined values.

## Practical Verification Pattern

During rollout, verify in layers:
1. `npm run type-check`
2. targeted unit/source tests for new primitives
3. targeted source tests for migrated routes
4. broader regression tests only after each group settles
5. runtime/manual verification for keyboard + safe-area behavior on actual devices

## Android Runtime Automation Pattern

If the project already has a partial Appium/WebdriverIO harness, do NOT discard it and start over.

Instead, normalize it for agent use with wrapper scripts and a focused smoke suite.

### Recommended wrapper layer
Create scripts such as:
- `tests/appium/scripts/env-android.sh`
- `tests/appium/scripts/check-device.sh`
- `tests/appium/scripts/start-appium.sh`
- `tests/appium/scripts/run-ui-foundation-smoke.sh`

The wrapper layer should standardize:
- `ANDROID_HOME`
- `ANDROID_SDK_ROOT`
- `PATH` to include platform-tools
- `ADB_BIN`
- `APPIUM_BIN`
- target device UDID
- app package/activity
- APK paths
- Appium port

### Why this matters
In brownfield remote-machine setups, the usual failure is not missing infrastructure but missing environment normalization.
Typical example:
- `adb` exists at a stable absolute path like `$HOME/Android/Sdk/platform-tools/adb`
- Appium exists in a user-local global npm bin like `$HOME/.npm-global/bin/appium`
- both fail from agent sessions because PATH is incomplete

A wrapper layer makes future agent runs deterministic.

### Device check expectations
A good `check-device.sh` should verify all of:
- adb binary exists and is executable
- target device appears in `adb devices -l`
- target device is in `device` state, not `unauthorized` or `offline`
- Appium binary exists and is executable
- Appium driver list shows `uiautomator2` installed

### Smoke-runner expectations
A good `run-ui-foundation-smoke.sh` should:
1. source env wrapper
2. run device/tooling checks
3. start Appium if needed
4. install test deps if needed
5. prefer a self-contained release APK by default, building it if missing
6. only fall back to debug APK when Metro-dependent debugging is explicitly desired
7. run a focused WDIO spec such as `ui-foundation.smoke.spec.js`

Why: in real agent runs, debug APKs can surface redbox failures like "Unable to load script" if Metro/bundling assumptions are wrong. Using the release APK removes that whole class of false-negative runtime failures.

### First-suite strategy
Start with anonymous-safe deep-linkable flows first:
- root tab shell visible
- add-item opens and save CTA is reachable
- manual-entry opens and save CTA is reachable
- settings shell opens
- manage-household shell can be captured

Do NOT try to automate every authenticated/shared-state flow in the first suite.
Stabilize the harness on simple deterministic routes first.

Important nuance from device verification:
- deep-linking directly into a form route is excellent for checking layout/runtime visibility
- it is NOT sufficient proof for navigation behavior that depends on real stack context, such as `router.back()` after save

So split the claims honestly:
- deep-link spec can verify header/footer/keyboard/picker/preset reachability
- a separate in-app navigation spec is needed to verify post-save return behavior or toast/screen transitions that rely on the existing stack

### Selector reality check
Do not assume React Native `testID` values will always be exposed to Android/Appium as `resource-id` selectors in the built app.
A migrated brownfield screen can still fail on-device even when source-level tests pass if the WDIO spec expects selectors like:
- `new UiSelector().resourceId("item-name-input")`

and the live hierarchy exposes the element differently.

When the first smoke run fails this way:
1. treat it as a spec/selector drift issue, not proof the infra is broken
2. inspect the live page source / screenshot artifacts from the failed run
3. update the spec to match the real exported selector shape (`text`, `description`, or actual resource-id)
4. rerun until the anonymous-safe smoke paths are stable

Concrete example from Stowsy:
- some form controls did expose usable `resource-id` values from `testID`
- tab bar buttons were easier to target by `content-desc` / accessibility description like `Inventory`
- a mixed selector strategy was the correct real-device approach, not a pure `resource-id` strategy

A first failing smoke run is acceptable if it proves the harness can:
- build/install the APK
- connect to the real device
- launch the app
- produce actionable artifacts for selector correction

### Real-stack verification pattern
After the anonymous-safe deep-link smoke suite is stable, add at least one broader real-stack spec.

Recommended pattern:
1. enter through a real tab or screen CTA
2. create or open state from inside the app flow itself
3. verify the destination migrated screen in true navigation context
4. only then claim stack-dependent behavior is runtime-covered

Good example:
- Inventory tab
- tap Add Item CTA
- save a real anonymous item
- return into inventory context
- open Edit Item from the saved row
- verify footer actions / sheet open-close behavior there

Important assertion lesson:
- do NOT use the newly entered item name by itself as proof that save/navigation succeeded
- that text can still be present on the source form if the route has not changed yet
- instead, wait for destination-specific signals such as the inventory row in the list, the destination screen title, or destination-only footer actions like `Save Changes`, `Delete`, or `Record Outcome`

This catches navigation-context issues that deep-link-only specs cannot prove.

### Sheet dismissal lesson
If a shared bottom sheet opens successfully but a backdrop click does not reliably return the app to the expected state in automation, prefer the explicit in-sheet cancel action for the stable gate.

Reason:
- backdrop dismissal can be gesture/timing-sensitive in Appium
- explicit `Cancel` proves the shared sheet is usable and dismissible without adding avoidable flakiness

Use backdrop dismissal as an extra check later, not the first stable release gate.

### Artifact discipline for runtime automation
Every failing smoke run should leave artifacts that future agents can inspect:
- screenshots
- page source / hierarchy dumps
- Appium server log
- optional logcat slice

This converts runtime failures into actionable debugging inputs instead of requiring a human to restate the failure.

### Key lesson
A first smoke suite that fails is still progress if it proves:
- the device is connected
- Appium launches
- the APK builds and installs
- WDIO reaches the app
- the harness can catch real route/selector mismatches

Treat that as working infrastructure with unstable specs, not as failed infrastructure.

## Continuation Discipline

After each rollout group, update continuation docs with:
- exactly what primitives were added
- which screens were migrated
- which tests passed
- which groups are still incomplete
- the exact next resume point

Do not mark the phase complete while later groups are still pending.

## Anti-Patterns

Avoid:
- adding blur before shell/layout stability exists
- mixing new primitives with many untouched bespoke modal patterns and then calling the UI system unified
- spending too long trying to make modal render tests perfect when source-contract tests would unblock progress faster
- broad full-app visual restyles before duplicated form routes are consolidated
- claiming completion after Group A if Groups B/C verification has not run
- getting stuck in verification loops after the foundation is already proven stable enough for the user's current goal

### Scope-control lesson
If the user says the app is already working and wants UI/UX progress, stop expanding runtime-verification scope unless a new UI slice actually needs it.

In that situation, the right move is usually:
1. keep validation to type-check + targeted non-runtime regression tests
2. continue with the planned phase order
3. make the next UI slice carefully and behavior-preservingly
4. report any still-unverified runtime claims honestly without turning them into the main task

This prevents the workflow from drifting away from the real objective: UI/UX implementation.

## References

- `references/haven-bottom-tab-safe-area-2026-05-07.md` — session example of fixing a floating React Navigation bottom tab bar that overlapped Android native navigation by deriving height/margin/padding from `useSafeAreaInsets()` and verifying with screenshot/XML bounds.
- `references/haven-floating-tab-scroll-overlap-2026-05-08.md` — follow-up audit showing that native-navigation clearance is not sufficient when scroll content still renders under the floating tab shell; includes XML-bound evidence and reusable verification checklist.

## Completion Standard

This rollout is working when:
- root/tabs/screen/footer shells are inset-aware
- critical form routes use a shared scaffold
- major picker/sheet patterns sit on shared overlay primitives
- type-check passes
- targeted tests pass
- continuation docs truthfully show what is done vs still pending
