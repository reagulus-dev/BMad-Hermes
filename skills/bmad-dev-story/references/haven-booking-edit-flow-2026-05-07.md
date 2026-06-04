# Haven booking edit flow — 2026-05-07

## Context

Haven Story 4.6 implemented internal booking edit from the Bookings tab after booking creation, overlap prevention, Today operations, and check-in/check-out status transitions were already in place.

## Implementation Pattern

Service layer:
- Add `updateInternalBooking(input)` next to booking creation/status-transition helpers.
- Scope the target row by both `bookingId` and `establishmentId` before updating.
- Validate the selected Room & Unit belongs to the same establishment, is `active=true`, and has `archived_at is null`.
- Reuse strict real date-only validation, not regex-only validation.
- Require `check_out_date > check_in_date`.
- Let DB overlap constraints remain authoritative for blocking booking conflicts, but map constraint/conflicting-key errors to a user-facing conflict message.
- Support optional quote mutation:
  - blank/null amount removes booking price rows
  - existing quote gets updated when present
  - new quote gets inserted when amount is present and no quote exists
  - duplicate quote rows should be cleaned or normalized if encountered

UI layer:
- Add one Edit action per booking row with stable `testID` such as `booking-edit:<id>`.
- Reuse the create form in edit mode instead of creating a separate divergent form.
- Prefill guest, room, dates, status, quote price/currency, and notes.
- Change form title/action from Add booking to Edit booking / Save booking.
- Provide a Cancel action that exits edit mode and resets form state without mutating the row.
- Refresh the booking list after save and prove the edited row displays updated values.

## Validation Pattern

Run the usual static/build checks:
- `npm run typecheck`
- `npm test` (noting if it aliases typecheck)
- `npx expo install --check`
- `npx expo export --platform web --output-dir /tmp/<flow>-web-export`

Live service smoke should prove more than “row updated”:
- fresh auth session + establishment fixture
- active Room A and active Room B
- archived/inactive room fixture for negative lookup
- create initial booking
- create same-room or target-room blocker when testing conflict rejection
- update booking fields: guest, room, dates, status, notes
- change quote price/currency
- remove quote price
- prove overlapping blocking edit is rejected
- prove archived/inactive rooms are not eligible through active-room lookup/service validation

Browser runtime QA should prove the actual operator flow:
- create room + booking
- click Edit
- change a field then Cancel, and verify no mutation
- click Edit again
- change guest/date/status/price/notes
- Save and verify refreshed row values
- remove quote and verify the price display disappears
- capture screenshots/HTML and console errors in `_bmad/artifacts/evidence/browser-booking-edit-<run_id>/summary.json`

Android release smoke still matters for packaging:
- rebuild final release APK after code changes
- install on target device
- launch and capture package/focus/PID
- label this as build/install/launch smoke unless full native edit interaction is exercised.

## Review Notes From This Slice

PASS WITH NOTES was appropriate because:
- acceptance criteria were met for active bookings and active rooms
- browser/service evidence covered the risky edit paths
- Android evidence was launch smoke only, not full native interaction automation
- booking update and quote mutation happen as multiple client-side calls, not a transaction/RPC
- if a booking’s existing room has since been archived, edit mode cannot preselect that inactive room and requires choosing an active room; this matches the active-room policy but is a UX edge case against a literal “room prefilled” criterion

## Reusable Pitfalls

- Do not claim quote edit is atomic if booking and price updates are separate client calls; recommend an `update_internal_booking_with_optional_price` RPC for future hardening.
- Do not treat create-flow validation as sufficient for edit flows; edit needs cancel/no-mutation, prefill, save/refresh, conflict rejection, inactive-room rejection, and quote removal evidence.
- Do not let archived rooms remain selectable in edit mode unless product explicitly permits editing historical bookings in inactive rooms.
- When testing text removal in React Native Web, prefer visible-state checkpoints plus screenshots/HTML over global body-text absence if hidden/stale DOM can retain old strings.
