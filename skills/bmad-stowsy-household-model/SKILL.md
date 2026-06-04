---
name: bmad-stowsy-household-model
description: Stowsy household product model — single-HH per user, explicit HH creation on signup, was_kicked_at kick detection. Session 2026-04-08 (updated).
category: software-development
tags: [stowsy, product-model, household, migration, auth]
---

# Stowsy Household Model — v2 (Post-Migration 013)

## Core Rule: One HH Per User — Explicit Creation

**Migration 013** changed the foundational rule: NO auto-household on signup.

```
Sign up
  → public.users row created
  → Redirect to /setup-household
       → User explicitly creates or joins HH
```

`handle_new_user()` DB trigger NO LONGER creates a personal HH automatically.

## was_kicked_at Flag

**Purpose:** Detect when a user was kicked from a shared HH so the app can show the appropriate prompt on next login.

**DB:** `public.users.was_kicked_at TIMESTAMPTZ NULL` (migration 018)

**Set by:** `remove_member_and_recreate_personal` RPC

**Flow:**
```
User KICKED from shared HH
  → RPC sets was_kicked_at = NOW()
  → RPC removes the membership and leaves the user with NO household
     (do NOT auto-create a replacement personal HH on kick)
  → Next login: auth store detects was_kicked_at + null householdId
  → Redirect to /setup-household?kicked=1
  → Kicked variant: amber banner, create-only, no join option
  → On success: clearWasKicked() called, redirect to inventory
```

## Auth Routing (getCurrentUser + fetchUserPublicProfile)

```typescript
// authService.ts — concurrent fetch of both signals
async function fetchUserPublicProfile(userId): Promise<{
  householdId: string | null   // from household_members
  wasKickedAt: string | null   // from public.users
}> { ... }
```

**Routing table (in `(tabs)/_layout.tsx`):**

| Condition | Destination |
|-----------|-------------|
| `!isInitialized` | wait |
| `!user` | not in tabs (redirect to login) |
| `user.householdId` | normal inventory |
| `!user.householdId && user.wasKickedAt` | `/setup-household?kicked=1` |
| `!user.householdId && !user.wasKickedAt` | `/setup-household` (normal) |

Important rule learned during stabilization:
- tabs routing must redirect ALL authenticated users with `householdId === null` into setup-household
- the kicked flag only chooses the kicked variant vs normal variant
- do not restrict the redirect logic to kicked users only, or normal signed-in/no-household accounts can fall through into tabs in an invalid state

Important follow-through learned during barcode/item-entry work:
- this routing rule is not enough by itself; item-entry save flows must also respect the explicit setup model
- do NOT let `add-item`, `scan/manual-entry`, or `scan/barcode-result` silently create/get a household during save
- if a signed-in user reaches an item-entry flow with `householdId === null`, the save path must return a `needs_household_setup` outcome and route to `/setup-household`
- this avoids architectural drift where routing says "explicit setup required" but save handlers revive hidden auto-create behavior

## setup-household — Three Entry Points

```
/setup-household            → normal onboarding (create + join)
/setup-household?kicked=1   → kicked user (amber banner, create only)
/setup-household?token=x    → invite accept (redirects to /join-household?token=x)
```

## Migration on Join

```
User joins household (from invite)
  → /join-household?token=x
  → If user has personal HH items → migration step (select what to bring)
  → joinHouseholdWithMigration RPC
       → If no current HH: insert membership into target HH
       → If already in target HH: idempotent success
       → If current HH is PERSONAL: migrate/delete old personal HH, then join target HH
       → If current HH is another SHARED HH: reject explicitly
```

### Critical RPC rule for single-HH transitions

In Stowsy's single-household model, invite acceptance must NOT reject the user just because they already belong to a different household. That would incorrectly block the normal case where the user currently has a personal HH and is trying to replace it by joining a shared HH.

The correct server-side rule is:
- reject only when the user is already in a different shared household
- allow transition when the current household is the user's personal household
- treat "already in target household" as idempotent success

Implementation guidance for `join_household_with_migration()`:
- determine the user's current HH before raising any `ALREADY_MEMBER_*` error
- classify that current HH as personal vs shared
- if personal, run migration/delete of the old HH first, then insert target membership
- do not insert target membership first and then try to discover the old HH afterward; that ordering can fight the single-HH model and mask the real transition case

## Household Model Rules

| User state | `is_shared` | Behavior |
|------------|-------------|----------|
| Personal HH | false | Free, solo, no invites |
| Same HH after first invite send | true | Pro required to SEND invites; do not create a second HH |
| Non-Pro joins shared HH | true | Migration step, personal HH deleted |
| User leaves shared HH | N/A | Personal HH re-created by RPC |
| User kicked from shared HH | N/A | Same as leave + was_kicked_at set |

## Creation Path — Drift Cleanup Rule

If household creation starts failing with `42501` / RLS on `households`, first check whether app code drifted back to direct client inserts such as:

```typescript
supabase.from('households').insert(...)
```

For Stowsy's canonical single-HH model, `createHousehold()` should NOT branch into separate personal/shared create paths. The stable path is:

```typescript
supabase.rpc('get_or_create_personal_household', {
  p_user_id: userId,
  p_user_email: '',
})
```

Then fetch the resulting household row and return it.

Important implementation detail discovered later:
- the RPC currently defaults to `My Home` when passed an empty email string
- if the UI lets the user name the household during setup, `createHousehold(name, userId)` must explicitly preserve that requested name after the RPC call (for example by renaming the returned household when needed)
- otherwise the setup-household text input is a lie and users silently get `My Home`

This preserves:
- one HH per user
- `is_shared` flip on invite send
- no revival of stale `personal: false` / shared-create logic
- no fragile client-side RLS dependency during post-signup session timing
- explicit setup-household naming behavior that matches the UI promise

## Pro Gate (Revised — ManageHouseholdScreen)

- **Household create**: always allowed (personal HH is free)
- **Invite send**: requires Pro — gated in `ManageHouseholdScreen` via upgrade modal
- **Invite accept**: NOT gated (anyone can accept a valid invite)

**Old screen (`HouseholdSettingsScreen` at `/household-settings`):**
- Conflicted the "no household" empty state with the Pro gate
- `handleCreateAndInvite` created a personal HH then immediately opened the invite modal — non-Pro users saw their HH created successfully then immediately hit the Pro gate

**New screen (`ManageHouseholdScreen` at `/manage-household`):**
- Pro gate is ONLY on the invite action — not on viewing members, editing name, or creating household
- Invite button subtext explicitly says "Pro required — tap to upgrade" when !hasPro
- After personal HH creation, NO auto-open of invite modal — clean separation
- Canonical runtime action model is intentionally simple:
  - **Personal HH (single member):** Rename + Invite only; NO Leave/Disband action
  - **Shared HH, current user = owner:** Rename + Invite + Remove others; NO Leave action; helper text: "To stop sharing, remove other members."
  - **Shared HH, current user = member:** Leave Household only; NO Rename/Invite/Remove actions
  - **Invited but not yet joined:** join-flow actions only (Join / Start Fresh / Cancel); NO Leave action before membership exists
- UI should treat visible role behavior as **owner vs member only**. If `admin` appears from schema/history, map it to member behavior in the current product/UI model rather than exposing a third action set.
- Do NOT expose a single-member `Disband Household` action. In the current single-household-required model that action is product drift because the app must always keep the user in some household context.
- Add **service-layer runtime guards** so future UI drift cannot bypass the model:
  - only owner can rename household
  - only owner can send invites
  - only owner can remove other members
  - owner cannot use the member leave path; owner should instead remove other members to stop sharing
  - leaveHousehold should preserve Supabase error code/message for debugging when the RPC itself fails

## Screens & Routes

| Route | Screen | Purpose |
|-------|--------|---------|
| `/manage-household` | `ManageHouseholdScreen` | Primary HH management — create/name/members/invite |
| `/household-settings` | `HouseholdSettingsScreen` | Orphaned — no longer linked from anywhere |
| `/setup-household` | `SetupHouseholdScreen` | Onboarding — create or join (first time) |

**Settings card:** "Household" section → "Manage Household" → navigates to `/manage-household` (no longer "Inventory Sharing").

## RLS / RPC Guardrails

Two critical hardening rules discovered during final stabilization:

- `public.users` read policy must preserve **self-read** in addition to same-household profile reads. If the policy only allows same-household reads, then freshly signed-up users or kicked users with no household can no longer read their own `display_name` / `was_kicked_at`, which breaks auth routing.
- SECURITY DEFINER household RPCs that accept `p_user_id` must verify the caller explicitly (`auth.uid() = p_user_id` for self-service flows, or owner-membership checks for admin/kick flows). Do not trust caller-supplied user IDs just because the RPC is only called from app code.

## Schema Key Points

- `households.is_shared`: canonical DB field for sharing state
- `inventory_items.household_id`: source of truth for item location
- `inventory_items.owner_id`: migration annotation only — do NOT use in new queries
- `public.users.was_kicked_at`: kick detection signal (null = normal)
