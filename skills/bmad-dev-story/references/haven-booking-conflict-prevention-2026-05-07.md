# Haven booking conflict-prevention slice — 2026-05-07

Reusable class: Supabase-backed booking/reservation overlap prevention with Android UI evidence.

## Problem shape

After a booking-create slice exists, the next safe slice is server-side conflict prevention before calendar/availability display. Successful booking creation must not imply double-booking protection.

## Implementation pattern that worked

- Add explicit product rules to the story:
  - blocking statuses: `tentative`, `confirmed`, `checked_in`
  - non-blocking statuses: `cancelled`, `checked_out`
  - date semantics: `[check_in, check_out)` so same-day checkout/check-in is allowed
- Add DB-level race/bypass protection, not only an RPC pre-check:
  - enable `btree_gist`
  - add a partial exclusion constraint on `room_unit_id` + `daterange(check_in_date, check_out_date, '[)')`
  - constrain only blocking statuses
- Replace/update the booking-create RPC so it:
  - keeps membership, active-room, date, and price validations
  - pre-checks overlaps using the same `[)` semantics
  - catches `exclusion_violation` and raises the same friendly conflict message
- In the React Native service wrapper, convert Supabase RPC errors into `Error` instances:
  - `throw new Error(error.message || 'Could not create booking.')`
  - This matters because UI catches may otherwise render a generic fallback and hide the server conflict text.

## Service smoke bundle

Use a fresh auth/session fixture and verify:

1. baseline confirmed/tentative booking creates
2. adjacent booking where prior `check_out_date == next check_in_date` is allowed
3. overlapping booking for the same room/unit is rejected by RPC
4. cancelled overlap is allowed
5. checked-out overlap is allowed
6. overlapping booking for a different room/unit is allowed
7. direct table insert/bypass overlap is rejected by the DB constraint
8. migration is listed locally and remotely
9. sign-out/cleanup where practical

Label this as service-path verification, not UI proof.

## Android UI QA pattern

When user asks for Android QA after conflict implementation:

- Rebuild the final release APK after the last UI/service error-surfacing fix.
- Install it on the target device before Appium claims.
- Use a seeded QA account/establishment/room if account creation is not the story under test.
- Add stable `testID` / accessibility IDs before building if the screen lacked them.
- Exercise both:
  - Story 3.1 positive booking creation visible on-device
  - Story 3.2 adjacent booking allowed and overlapping booking rejected with the visible conflict message
- Evidence bundle should include screenshots, Appium page source/XML, Appium log, redacted `summary.json`, APK hash/size, and device ID.

If WDIO is not installed in the project, a temporary raw WebDriver/Appium HTTP client is acceptable for focused evidence. Keep scripts credential-safe and delete temporary runners/seeders before final handoff unless they are promoted into maintained test assets.

## Pitfalls

- Do not start calendar/availability display before conflict prevention exists.
- Do not claim conflict prevention from client-side filtering or RPC-only checks.
- Do not treat APK build/install as UI runtime proof.
- Android keyboard / ADB text-entry automation may open Samsung keyboard settings or fail focus; Appium `setValue` through UiAutomator2 is often more reliable for focused form proof.
- Capture the actual visible conflict text in runtime XML/page source; a generic `Could not create booking.` means the UI is not surfacing the server contract yet.

## Good final status wording

`Story 3.2 implemented, remotely migrated, service-smoke verified, code-reviewed PASS, and Android UI runtime-verified for booking creation plus adjacent/conflict flows. Browser interactive flows and iOS runtime remain pending.`
