# Android release runtime QA pattern for Expo/React Native BMad stories

Use this when a BMad story touches mobile UI flows and Android runtime evidence is required. This reference was distilled from a Haven Expo/React Native session on a Samsung Galaxy S10.

## Why this matters

A debug/dev-server launch can prove useful interaction, but founder-facing runtime claims should prefer the shipped-style artifact when possible. For Expo/React Native, a clean release APK run plus UIAutomator screenshots/XML and logcat inspection gives stronger evidence than a Metro-only smoke.

## Preferred evidence bundle

1. Pre-runtime gates:
   - `npm run typecheck`
   - `npm test` when meaningful; if it aliases typecheck, say so
   - `npx expo install --check`
2. Build the release APK:
   - `cd android && ./gradlew assembleRelease`
3. Capture artifact identity:
   - `sha256sum android/app/build/outputs/apk/release/app-release.apk`
   - `stat -c 'size_bytes=%s mtime=%y' android/app/build/outputs/apk/release/app-release.apk`
4. Install the release APK on the target device:
   - `$HOME/Android/Sdk/platform-tools/adb -s <serial> install -r android/app/build/outputs/apk/release/app-release.apk`
5. Start from a clean app state for setup/auth/onboarding flows:
   - `$ADB -s <serial> shell pm clear <package>`
   - then launch with `monkey -p <package> -c android.intent.category.LAUNCHER 1`
6. Exercise the real user path with ADB/Appium/manual input.
7. Capture evidence after each meaningful state:
   - screenshot: `adb shell screencap -p /sdcard/<name>.png && adb pull ...`
   - XML: `adb shell uiautomator dump /sdcard/<name>.xml && adb pull ...`
8. Inspect logcat before declaring a pass:
   - clear before run: `adb logcat -c`
   - save full log after run
   - grep for `ReactNativeJS|AndroidRuntime|FATAL|Exception|Could not|Unable|Error`
   - explicitly report whether fatal JS/native markers were absent
9. Copy artifacts into project-local BMad evidence, e.g. `_bmad/artifacts/evidence/android-runtime-qa-<run_id>/`.
10. Append QA evidence to the relevant story file(s), update `_bmad/state.json`, `CONTINUE-HERE.md`, and current plan/status docs.

## Evidence assertions to record

For each screen/flow, record both action and observed UI text/state from the runtime XML/screenshots. Example pattern:

- Auth launch showed `Haven`, `Sign in`, `Email`, `Password`, `Create account`.
- Setup appeared with `Set up Haven`, `Establishment`, `Create establishment`.
- Home shell appeared with the active entity name.
- Target tab showed the expected empty state and form controls.
- Final state showed the newly created row plus key metadata.
- Logcat had no `FATAL EXCEPTION`, no `Unable to load script`, and no fatal JavaScript exception.

## Pitfalls

- Do not claim a release/runtime pass from an initial debug APK or Metro session unless that is explicitly the target build.
- Do not let a successful service-layer smoke substitute for UI runtime evidence; record it separately.
- Do not leave a detached Metro process running after moving to release APK verification.
- If a terminal tool blocks long-running Metro commands, do not retry the same command verbatim; use a detached process only long enough to complete debug investigation, then stop it.
- UIAutomator XML can encode `&` as `&amp;`; account for that when checking text like `Rooms & Units`.
- When using generated runtime test accounts, redact or avoid preserving passwords; artifact metadata should contain non-secret identifiers only.
