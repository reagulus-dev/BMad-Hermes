# Haven availability operations slices — 2026-05-07

Use this as a compact reference for Supabase-backed availability operations in Expo/React Native BMad stories.

## Slices covered

- Availability block create/edit.
- Today operations display.
- Availability block deletion/clearing.

## Useful implementation pattern

- Keep availability reads and block mutations in one service layer when they share semantics (`availabilityService.ts` in Haven).
- Use `[start_date, end_date)` semantics for availability blocks, matching booking `[check_in, check_out)` behavior.
- Validate date-only values as real calendar dates, not only with a `YYYY-MM-DD` regex.
- Restrict block create/edit room choices to active, unarchived room/unit rows in the UI/service path.
- Before creating or updating an availability block, service-smoke both conflict classes:
  - same-room blocking booking overlap should reject
  - same-room availability block overlap should reject, excluding the edited block when editing
- For block clearing, scope the delete by both tenant/establishment and block ID and report not-found/delete-count failures.
- If the schema has no `active`, `cleared_at`, or audit table for blocks, label the clear behavior honestly as hard delete and defer soft-delete/audit explicitly.

## Today operations display pattern

- Derive the operating date from the establishment/tenant timezone, not raw UTC.
- Separate Today buckets by product semantics:
  - arrivals: `check_in_date == today` and operational statuses that have not checked out/cancelled
  - departures: `check_out_date == today` excluding cancelled
  - in-house: `check_in_date <= today < check_out_date` and `confirmed`/`checked_in`
  - blocked: availability blocks with `start_date <= today < end_date`
- Derive capacity/count cards from the existing availability read model so Today and Calendar agree.
- Reload Today on tab focus when Calendar can mutate availability/block state.
- Clear prior Today state at load start to avoid stale rows after reload failure or tenant switch.

## Runtime evidence pattern

A strong combined smoke for these slices verifies:

- fresh auth/tenant fixture through the intended setup path
- multiple active room/unit fixtures
- booking fixtures for arrival, in-house, and excluded cancelled cases
- availability block visible before clearing
- Today displays arrival plus block distinctly
- Calendar clear/delete removes the block
- Today after returning preserves bookings but no longer displays the cleared block
- browser console/page errors are zero
- Android build/install/launch smoke is recorded separately from Android UI interaction

## Honest boundaries

- `npm test` may be only typecheck in early Expo projects; say so and rely on service/browser/runtime evidence for behavior.
- Browser runtime QA can prove web UI flow, but Android launch smoke is not the same as Android UI interaction.
- Service-path overlap checks are not transactional DB-level race protection unless backed by constraints/RPC locks/triggers.
- Direct DB audit/soft-delete history is deferred unless the schema includes a real audit/soft-delete mechanism.
- iOS runtime launch remains a separate cross-platform gate.
