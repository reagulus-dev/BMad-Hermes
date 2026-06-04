# Haven Story 3.1 — Booking Create Slice Pattern

Session-specific reference for a Supabase-backed booking/reservation create story. Keep the class-level rules in `SKILL.md`; use this as a concrete example when implementing similar accommodation/bookable-resource flows.

## Story Shape

- Product: Haven accommodation booking app.
- Story: `3.1 — Add Booking Flow`.
- Scope: create internal booking with guest, active Room & Unit, check-in/check-out, status, optional price, and notes.
- Deliberately out of scope: overlap/conflict prevention, deferred to Story 3.2.

## Implementation Pattern

- Add an RPC for booking creation when creation spans multiple invariants or child records:
  - require `auth.uid()`;
  - verify establishment membership;
  - require an active, unarchived bookable room/unit in the same establishment;
  - validate guest name, supported status, `check_out_date > check_in_date`, and non-negative optional price;
  - insert booking with internal source;
  - insert optional `booking_prices` record with `label = 'quote'`, not payment state.
- Add a client service that mirrors the cheap validation:
  - date-only `YYYY-MM-DD` checks;
  - explicit `check_out > check_in` guard;
  - invalid numeric input should error, not silently become `null`;
  - normalize currency casing/default.
- In UI, keep the list + form scrollable and tenant-scoped:
  - load active bookable units and bookings together;
  - reset selected room/unit from the fresh active list when establishment changes;
  - display optional price using nullish checks so `0.00` is not hidden.

## Service-Path Smoke Shape

Use a fresh Auth session without printing secrets, then:

1. Create establishment through intended setup RPC.
2. Create an active room/unit.
3. Create booking through the new RPC/service path.
4. Verify optional price exists as a quote record.
5. Attempt same-day check-in/check-out and expect rejection.
6. Create inactive/archived room/unit and expect booking rejection.
7. Read/list bookings for the establishment and verify the expected booking is visible.
8. Sign out.

Label this as live Supabase service-smoke, not browser/device UI verification.

## Evidence Wording

Good status wording:

`implemented, reviewed PASS WITH NOTES, live Supabase service-smoke verified, Android release build/install verified, UI runtime pending`

Explicitly list unverified areas:

- Android booking creation UI interaction.
- Browser interactive form flow.
- iOS runtime launch.
- Conflict/overlap prevention if deferred.

## Review Notes from the Session

Non-blocking findings worth checking in future booking forms:

- Invalid typed price like `abc` should not create a booking with a missing price.
- Valid zero-value quotes should display; avoid `if (!amount)` style checks.
- Stale selected room/unit should reset when the active establishment changes.

## Validation Commands Used

- `npm run typecheck`
- `npm test`
- `npx expo install --check`
- `npx expo export --platform web --output-dir /tmp/<app>-booking-web-export`
- `npm audit --audit-level=high`
- `npx supabase db push`
- `npx supabase migration list`
- Android release build/install as packaging evidence only, not UI flow evidence.
