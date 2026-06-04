# Haven Rooms & Units edit/archive slice — 2026-05-07

Session-specific reference for applying `bmad-dev-story` to a small Supabase-backed CRUD edit/archive slice.

## Context

Project: `/home/reagulus/projects/Haven`
Story: Epic 2 / Story 2.2 — Edit/archive Rooms & Units.

Acceptance criteria:
- user can edit Room & Unit fields
- user can archive a Room & Unit
- archived units do not appear as bookable but remain attached to history

## Implementation pattern

Files changed:
- `src/services/roomUnitService.ts`
- `src/features/rooms/RoomsUnitsPanel.tsx`

Service pattern:
1. Keep update/archive calls in the service layer, not directly in UI.
2. Reuse normalization for create/update fields: trimmed display name, optional type/notes, minimum capacity.
3. Scope update/archive by parent tenant/establishment ID as well as row ID.
4. For edit of active inventory, filter `active = true` and `archived_at is null` so stale archived rows cannot be edited through the active path.
5. Archive non-destructively: set `active = false` and `archived_at = now/ISO timestamp`; do not delete rows that may be referenced by bookings/history.

UI pattern:
1. Add per-row `Edit` and `Archive` actions to the active list.
2. Reuse the existing compact add form as edit state when the screen is intentionally lightweight.
3. Provide a cancel path for edit state.
4. Confirm archive with copy that explains the unit stops being bookable but remains attached to history.
5. Remove archived rows from the active list after archive succeeds.

## Verification pattern

Commands used:
- `npm run typecheck`
- `npm test`
- `npx expo install --check`
- `npx expo export --platform web --output-dir /tmp/haven-rooms-edit-archive-web-export`
- Android release build/install when a device run is planned

Live service-path smoke shape:
1. Fresh public Supabase Auth sign-up with immediate session.
2. Create establishment through intended `create_establishment_with_owner` RPC.
3. Insert active `room_units` fixture.
4. Update display name/type/capacity/notes with the same active/unarchived filters as the service.
5. Insert a historical fixture that references the room, such as a booking.
6. Archive the room via `active=false` plus `archived_at`.
7. Query active/bookable list and assert the archived room is absent.
8. Query the historical fixture and assert it still references the archived room.
9. Sign out or clean up where practical.

Evidence snapshot from session:
- `signUpSession=true`
- `establishmentCreated=true`
- `roomCreated=true`
- `roomUpdated=true`
- `roomArchived=true`
- `activeListExcludesArchived=true`
- `bookingStillReferencesArchivedRoom=true`
- `signOut=true`

## Android build/runtime notes

- On this machine, Gradle release builds may need explicit SDK env:
  `ANDROID_HOME=$HOME/Android/Sdk ANDROID_SDK_ROOT=$HOME/Android/Sdk ./gradlew assembleRelease` from `android/`.
- Android release build + APK install proves packaging/installability, not UI interaction.
- An ADB/uiautomator run can fail at Auth text input/submission even after a valid APK install. Record this as an automation/input limitation and keep UI runtime pending unless the actual edit/save/archive flow is observed.

## Status wording

Precise status used in `_bmad/state.json`:

`rooms_units_edit_archive_reviewed_service_verified_android_build_installed_ui_runtime_pending`

This correctly distinguishes:
- implemented and reviewed
- service-path runtime smoke verified, including history preservation
- Android release build/install verified
- Android UI edit/archive interaction still unverified
- iOS/browser interactive flows still unverified
