---
name: bmad-feature-retirement-clean-removal
description: Cleanly remove an abandoned product feature from a live app by inventorying all entry points, deleting implementation code, updating user-facing copy/routes, removing stale tests, and verifying the app still type-checks, builds, and installs.
---

# BMad Feature Retirement / Clean Removal

Use when a user has explicitly decided to abandon a feature and wants it removed cleanly rather than hidden.

## When to use
- A feature is being intentionally cut from the product
- The request is to "remove it entirely" or "scrape every code regarding X"
- Dead code paths, routes, tests, and docs should be deleted rather than left dormant
- You need strong verification that the app still works after removal

## Core principle
Do not start by deleting implementation files blindly. First inventory the full feature surface so removal is complete and does not leave broken routes, stale references, or misleading product copy.

## Workflow

### 1. Confirm product truth
Write down the new canonical product surface before touching code.
Example:
- remove Receipt Scanner entirely
- keep Barcode Scanner
- keep Manual Entry

This prevents accidental partial retention of old entry points.

### 2. Inventory the full feature surface
Use broad repo searches first.
Search for:
- route paths
- screen/component names
- service names
- marketing/product copy
- test IDs
- tests
- docs / continuation notes

Good search patterns:
- feature name in lowercase + PascalCase variants
- route fragments
- marketing phrases users actually see
- supporting subsystems (stores, parsers, downloaders, runtime managers, helpers)

For large removals, split inventory into:
- live app surface
- implementation/services
- tests
- docs

### 3. Remove user-facing entry points first
Update the visible app so it reflects the new product truth:
- tabs / menus
- home CTAs
- onboarding flows
- inventory empty states
- FAQ / upgrade / pricing pages
- deep links or router pushes

Prefer rewrites when the old file was feature-centric and patching would leave confusing residue.

### 4. Remove implementation files
Delete the retired feature’s:
- routes
- screens
- services
- stores
- AI/runtime/download helpers
- parsers / OCR helpers / adapters
- feature-specific types
- serverless/backend endpoints that existed only for that feature (for example Supabase functions)

Then run a search for the deleted symbol names and route paths to confirm zero live references remain.

For mobile/native feature removals, do not stop at `src/` cleanup. Also inspect and remove:
- `app.json` / Expo plugins and permission copy
- `package.json` dependencies that were only needed by the retired feature
- Android `AndroidManifest.xml` permissions, services, receivers, native-library declarations
- Android `MainApplication.kt` or package registration for custom native modules
- tracked plan/debug docs that still frame the removed feature as active

A feature can look removed in source and tests while still breaking release builds because an Expo plugin or native registration references a now-uninstalled package.

### 5. Remove or update tests
Treat tests in two buckets:
- tests for intentionally removed behavior → delete them
- source assertions for changed product truth → update them

Do not waste time fixing tests that verify functionality the user explicitly asked to remove.

### 6. Verify with layered checks
Run verification in this order:
1. source/reference searches
2. type-check
3. test suite (or targeted tests first, then broader suite)
4. platform build
5. install/smoke test on device if available

For React Native / Expo Android work, strong final checks are:
- `./node_modules/.bin/tsc --noEmit`
- `./node_modules/.bin/jest --runInBand`
- `./gradlew assembleRelease`
- `adb install -r <apk>`

If Android release build fails after dependency/plugin cleanup, read the exact failure before assuming the removal broke app logic.
Two important failure classes:
- stale Expo/native plugin references (for example `PluginError: Failed to resolve plugin for module ...`) → remove the leftover plugin/config entry
- Dex merge Java heap OOM during release packaging → this can be environmental; retry with higher Gradle heap (for example `GRADLE_OPTS='-Xmx4g -XX:MaxMetaspaceSize=1g' ./gradlew assembleRelease`) before concluding the code is still broken

If the suite still has failures, distinguish:
- removal-caused failures
- unrelated pre-existing failures

Do not block a valid feature retirement on unrelated red tests; document them explicitly.

### 7. Reconcile continuation docs
Update `CONTINUE-HERE.md` or equivalent so future sessions do not treat the retired feature as active work.
At the top, state the new truth plainly:
- feature intentionally removed
- what remains in product scope
- future revisit, if any, should start cleanly

## React Native / Expo-specific guidance
- Search both `src/app/...` routes and feature folders
- Search for route strings like `/scan/...` as well as component names
- Update onboarding and empty-state copy, not just navigation
- Check tests that assert source strings / route pushes / testIDs
- After large deletions, type-check and Android release build are the strongest sanity checks

## Useful command / search pattern examples
- broad source inventory:
  - `receipt|Receipt|local-ai|Local AI|scan/camera|scan/review|scan/local-ai`
- post-delete verification:
  - deleted route fragments
  - deleted component/service symbols
  - removed type names
- validation:
  - `./node_modules/.bin/tsc --noEmit`
  - `./node_modules/.bin/jest --runInBand`
  - `./gradlew assembleRelease`
  - `adb install -r <apk>`

## Pitfalls
- Hiding a feature in one screen but leaving old routes reachable elsewhere
- Forgetting onboarding, FAQ, pricing, or empty-state copy
- Leaving tests for intentionally removed functionality and treating them as regressions
- Updating references but forgetting to physically delete dead implementation files
- Leaving continuation docs claiming the removed feature is still active
- Assuming a patch tool’s lint output is authoritative; verify with direct type-check/build/test commands

## Evidence/reporting template
Report removal with:
- product truth after change
- files/routes deleted
- user-facing screens/copy updated
- post-delete search result summary
- type-check result
- test result, including unrelated residual failures if any
- build result
- install/smoke-test result

## When this skill paid off
This workflow was validated during Stowsy’s deliberate retirement of the entire Receipt Scanner surface, including AI-assisted Local AI receipt scanning. The clean-removal approach prevented route drift, stale tests, and misleading product copy while preserving barcode scan + manual entry and keeping the app buildable/installable.
