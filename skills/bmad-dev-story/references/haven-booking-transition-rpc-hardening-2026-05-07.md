# Haven booking transition RPC hardening — 2026-05-07

## Class of task

Booking/reservation operational status transitions where app screens expose actions such as check-in, check-out, cancel, and no-show, especially when earlier slices implemented service-path validation but review/user discussion flagged DB hardening as deferred.

## Reusable lesson

If status-transition hardening is only mentioned in chat or as a review note, treat it as not reliably planned. Persist it in BMad state/story `next_recommended_workflows` or implement it before building dependent workflow slices. In this session, the user explicitly asked whether check-in/check-out hardening was planned and would not be missed; because it was only a deferred note, the correct sequence was: harden transitions first, then build Today cancellation/no-show.

## Implementation pattern that worked

1. Add a shared transactional RPC such as `transition_booking_status(establishment_id, booking_id, action, operating_date, notes)` for all operational status changes.
2. Keep action rules explicit:
   - `check_in`: `tentative`/`confirmed`, operating date inside stay window.
   - `check_out`: only `checked_in`, operating date at/after departure rule as defined by product.
   - `cancel`: `tentative`/`confirmed` before operationalization.
   - `no_show`: `tentative`/`confirmed` only on scheduled arrival date unless the product says otherwise.
3. Add terminal status values deliberately, e.g. `no_show`, and update read models so terminal statuses are non-blocking for availability when that is the product rule.
4. Remove generic app-service status mutation for operational states. Generic booking edit/upsert should only directly create/change pre-operational statuses such as `tentative`/`confirmed`, while preserving existing operational statuses during detail edits.
5. Harden DB bypasses:
   - `BEFORE UPDATE OF status` trigger rejects status changes unless a trusted transaction marker/GUC is set.
   - transition RPC sets the trusted marker only around the status update.
   - upsert/create RPC rejects new operational/terminal statuses and rejects operational status changes.
   - optional defense-in-depth: `BEFORE INSERT` trigger rejects direct table inserts that start bookings in operational/terminal statuses.
6. Update UI:
   - Today shows action buttons only in eligible rows/buckets.
   - Today reloads after successful transition.
   - Bookings refreshes on focus if Today can mutate statuses that should be visible in the list.
   - Bookings status editor should not offer terminal/operational statuses directly if those are transition-managed.

## Validation pattern

Service/RPC smoke should prove both allowed paths and bypass rejection:
- check-in success
- check-out success
- repeated checkout rejected
- cancel success
- cancelled check-in rejected
- no-show wrong-date rejected
- no-show success
- unsupported action rejected
- direct status update rejected
- direct operational insert rejected
- upsert operational create rejected
- upsert operational update rejected
- terminal status is non-blocking for same-room rebooking when product rule says so

Browser/runtime QA should prove the operator flow:
- Today cancel/no-show actions visible for eligible arrivals
- cancel removes arrival from Today
- no-show removes arrival from Today
- terminal statuses visible in Bookings after focus/reload
- console errors captured and counted

Keep Android APK build/install/launch smoke separate from native UI interaction evidence. It proves packaging/installability, not the Today action flow.

## Pitfalls

- Do not count TypeScript union types as security or runtime safety; RPC and DB code still need unsupported-action guards.
- Do not leave status hardening as a loose chat note if the next slice depends on it.
- Do not let generic booking edit/upsert paths change bookings into `checked_in`, `checked_out`, `cancelled`, or `no_show` after adding a transition RPC.
- Do not forget direct insert bypasses; an update trigger alone does not prevent a row from being inserted directly with an operational status.
- Do not only verify that cancelled/no-show rows disappear from Today; also verify the terminal status remains visible in Bookings/history after refresh.
