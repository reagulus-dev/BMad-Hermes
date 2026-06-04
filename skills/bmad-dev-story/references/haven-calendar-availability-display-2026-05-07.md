# Haven Calendar / Availability Display — 2026-05-07

Class pattern: booking/reservation availability read-model story for a Supabase-backed Expo/React Native app.

## Context

Haven already had:
- active Rooms & Units
- booking creation via RPC
- server-side overlap prevention
- `availability_blocks` table in the initial schema
- BMad story/state/evidence conventions

The next slice made the Calendar tab show a 7-day availability view grouped by date and status.

## Implementation Shape

Added a service-layer read model rather than computing ad hoc in the component:

- list active bookable units
- fetch overlapping bookings for `[start_date, end_date)`
- fetch overlapping availability blocks for `[start_date, end_date)`
- create per-day cells grouped into `available`, `tentative`, `booked`, `checked_in`, and `blocked`

Rules captured in the service:

- blocking booking statuses: `tentative`, `confirmed`, `checked_in`
- non-blocking statuses: `cancelled`, `checked_out`
- date occupancy uses half-open ranges: `start <= date < end`
- blocks take display precedence over bookings for the same unit/date
- block creation/editing can be deferred, but block display should still be verified if the table exists

## UI Shape

The Calendar tab receives the active establishment and derives the first visible date from its timezone. The view is mobile-first/date-first:

- summary pills across the 7-day window
- Previous/Next week controls
- one card per date
- status groups per date
- room row with capacity/type and status badge
- explicit loading/error/empty copy

Use stable `testID` and `accessibilityLabel` values for browser/Appium probes: screen root, week buttons, summary pills, groups, and cells.

## Review Lessons

A focused review found two recurring issues worth checking in future availability stories:

1. Stale async loads: rapid week navigation can let a slower old request overwrite the selected newer window. Use cancellation flags, request IDs, or equivalent guards.
2. Timezone boundary: raw `new Date().toISOString().slice(0, 10)` means UTC “today”, not the establishment’s local operating date. Use `Intl.DateTimeFormat(..., { timeZone })` or an equivalent date-only helper.

## Validation Pattern

Run all normal app gates:

```bash
npm run typecheck
npm test
npx expo install --check
npx expo export --platform web --output-dir /tmp/<project>-calendar-web-export
cd android && ANDROID_HOME=$HOME/Android/Sdk ANDROID_SDK_ROOT=$HOME/Android/Sdk ./gradlew assembleRelease
```

Add a live service smoke that creates fixtures and verifies the read model:

- active rooms/units
- tentative booking
- confirmed booking
- checked-in booking
- cancelled booking that should not block
- checked-out booking that should not block
- availability block
- checkout-day boundary returns to available unless covered by another record

Add browser/runtime QA if native Appium is not economical for the exact screen; label it honestly as browser runtime evidence. Android build/install/launch smoke proves package health, not calendar interaction.

## Evidence Boundaries

Good final wording:

- “Calendar behavior browser/runtime-service verified.”
- “Android release build/install/launch smoke passed.”
- “Full Android Calendar interaction pass not performed.”
- “iOS runtime launch remains unverified.”

Avoid:

- “Android UI runtime verified” if only `monkey` launch/focus/PID was checked.
- “Availability complete” if blocks exist in schema but are not represented in display.

## Haven Evidence Example

- Story: `_bmad/artifacts/stories/4-1-calendar-availability-display.md`
- Consolidated evidence: `_bmad/artifacts/evidence/calendar-availability-display-20260507063917/summary.json`
- Browser runtime evidence: `_bmad/artifacts/evidence/browser-calendar-availability-20260507063527/summary.json`
- Android package: `app.appsfoundry.haven`
