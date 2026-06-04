# Haven housekeeping / room-ready status slice — 2026-05-07

Reusable pattern for room-readiness slices in Haven-style Expo/Supabase apps.

## Scope pattern
- Keep housekeeping/readiness separate from booking availability; dirty rooms do not automatically block saleable inventory unless a separate availability block exists.
- Store readiness on the room/unit row (`ready`, `dirty`, `cleaning`, `inspection`) plus an update timestamp.
- Expose a scoped RPC for readiness changes rather than mutating the room row directly from the app.
- On booking checkout, mark the checked-out active/unarchived room dirty inside the trusted booking transition RPC.

## Validation pattern
- Smoke default status on room create (`ready`).
- Smoke manual RPC cycle: `dirty -> cleaning -> ready` and inspection path if exposed.
- Smoke checkout path: confirmed booking -> check-in -> check-out -> room becomes `dirty`.
- Smoke invalid status rejection.
- Smoke inactive/archived room rejection.
- If direct-write hardening is desired, add a trigger guard and smoke direct `room_units.housekeeping_status` update rejection.
- Browser QA should prove Today card visibility, manual cycle, checkout dirtying, and console error count 0.

## Review notes
- A PostgreSQL custom GUC trigger guard is good enough for Supabase REST/RPC app flows, but not an absolute boundary for arbitrary SQL execution in the same transaction.
- Android build/install/launch smoke is packaging/runtime-shell evidence, not native Housekeeping UI interaction evidence.
