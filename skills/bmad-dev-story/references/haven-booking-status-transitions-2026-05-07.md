# Haven booking status transitions — 2026-05-07

Use this as a compact example for BMad booking/reservation status-transition slices.

## Story shape

- Story: `4.5 Check-in/check-out status transitions`.
- UI surface: Today operations tab.
- Service surface: `transitionBookingStatus(...)` in `src/services/bookingService.ts`.
- Product rule: operators can advance operational status, not edit payment/housekeeping/no-show flows in this slice.

## Implementation pattern

- Add a transition service scoped by `establishment_id` + booking ID before mutation.
- Validate operating date as a real date-only value, not just a regex string.
- Check-in:
  - allowed current statuses: `tentative`, `confirmed`
  - next status: `checked_in`
  - allowed date window: `check_in_date <= operating_date < check_out_date`
- Check-out:
  - allowed current status: `checked_in`
  - next status: `checked_out`
- Add an explicit runtime guard for unsupported actions even if TypeScript action unions already exist.
- In Today UI, show action buttons only in eligible buckets and use per-booking saving state.
- Reload Today after a successful transition so arrivals/in-house/departures and summary counts move with the status.

## Validation pattern

Run both state-machine service smoke and UI/runtime QA:

- Static/build:
  - `npm run typecheck`
  - `npm test` when available; label it honestly if it only aliases typecheck
  - `npx expo install --check`
  - `npx expo export --platform web --output-dir <tmp-export>`
- Service smoke:
  - create a fresh auth/session + establishment + active unit
  - create eligible confirmed/tentative booking and verify check-in becomes `checked_in`
  - create checked-in booking and verify checkout becomes `checked_out`
  - reject cancelled check-in
  - reject future/out-of-window check-in
  - reject repeated checkout
- Browser/runtime QA:
  - create fixture through the app UI where practical
  - verify Check in appears on Today arrival
  - click Check in and wait for Check out/in-house state
  - click Check out and verify active Today worklists no longer show the booking
  - capture screenshots/HTML and console errors in `summary.json`
- Android:
  - rebuild final release APK after review fixes
  - install and launch-smoke at minimum
  - do not label launch-smoke as full native interaction automation

## Review notes from this session

- Verdict was `PASS WITH NOTES` after service/browser/Android launch evidence.
- Non-blocking hardening: transition rules were service-path validation only; DB trigger/RPC state-machine constraints were deferred.
- Review caught that relying on TypeScript for action safety was weaker than adding a runtime unsupported-action guard; fix was applied and targeted validation rerun.
- Raw backend error messages could still surface in Today on unexpected failures; current custom validation errors were user-safe, but future hardening should map unexpected backend errors to generic UI copy.

## Evidence artifacts from example session

- Story anchor: `_bmad/artifacts/stories/4-5-check-in-check-out-transitions.md`
- Consolidated evidence: `_bmad/artifacts/evidence/check-in-check-out-transitions-20260507104839/summary.json`
- Browser QA: `_bmad/artifacts/evidence/browser-checkin-checkout-20260507104258/summary.json`
- Service smoke: `/tmp/haven-checkin-checkout-service-smoke-final.json`

## Honest boundaries

- Browser QA can prove the interactive web flow.
- Android build/install/launch smoke proves package health, not full native Today interaction.
- Service-path validation is not DB-level state-machine hardening.
- iOS runtime launch remains a separate cross-platform gate.
