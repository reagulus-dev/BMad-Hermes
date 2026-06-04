# Haven Rooms & Units slice — 2026-05-06

Session-specific reference for applying `bmad-dev-story` to a small Supabase-backed CRUD/list-create slice.

## Context

Project: `/home/reagulus/projects/Haven`
Story: Epic 2 / Story 2.1 — Rooms & Units list and create flow.

Acceptance criteria:
- view active Rooms & Units
- create Room & Unit with display name and capacity
- optional type/category and notes
- empty state routes into add flow

## Implementation pattern

Files changed:
- `src/services/roomUnitService.ts`
- `src/features/rooms/RoomsUnitsPanel.tsx`
- `src/features/tabs/MoreScreen.tsx`
- `App.tsx`

Class-level pattern:
1. Keep Supabase access in a service rather than direct UI calls.
2. Scope list/create calls by active parent tenant/establishment.
3. For “active” lists, filter both the boolean status and archive marker when the schema has both, e.g. `active = true` and `archived_at is null`.
4. Use an inline add form for a compact first slice when navigation is not yet mature.
5. If the list/form lives under an existing tab, make the tab content scrollable and keyboard/tap tolerant before accepting review.

## Verification pattern

Commands used:
- `npm run typecheck`
- `npm test`
- `npx expo install --check`
- `npx expo export --platform web --output-dir /tmp/haven-rooms-web-export-2`

Live service-path smoke shape:
1. Fresh public Supabase Auth sign-up with immediate session.
2. Create establishment through intended `create_establishment_with_owner` RPC.
3. Insert active `room_units` fixture with display name/type/capacity/notes.
4. Insert inactive + archived `room_units` fixture.
5. Query active list with the same filters used by the app service.
6. Assert the active list returns only the unarchived active fixture.
7. Sign out.

Evidence snapshot from session:
- `signUpSession=true`
- `establishmentCreated=true`
- `roomCreated=true`
- `activeRoomCount=1`
- `activeListOnlyIncludesUnarchived=true`
- `signOut=true`

## Review note that became a reusable pitfall

The first implementation passed typecheck/export and service smoke, but review noted that `MoreScreen` used fixed content. For mobile CRUD screens, this can break as rows grow or the keyboard opens. The fix was wrapping tab content in `ScrollView` with `keyboardShouldPersistTaps="handled"` and bottom padding, then rerunning typecheck and web export.

## Status wording

Precise status used in `_bmad/state.json`:

`rooms_units_slice_reviewed_runtime_service_verified_ui_device_pending`

This correctly distinguishes:
- implemented and reviewed
- service-path runtime smoke verified
- browser/device UI interaction still unverified
- Android/iOS launch still unverified
