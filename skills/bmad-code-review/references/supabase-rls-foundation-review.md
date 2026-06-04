# Supabase RLS Foundation Review Notes

Use when reviewing a BMad story that introduces or changes Supabase/Postgres schema, RLS policies, tenant membership, or setup/onboarding writes.

## Review checks learned from Haven setup foundation

- Check for recursive RLS policy paths:
  - Example risk: `establishments` policy queries `establishment_members` while `establishment_members` policy queries `establishments`.
  - Prefer `SECURITY DEFINER` helper functions with a fixed `search_path` for membership/ownership predicates.
  - Keep helpers small and stable; avoid broad table-returning functions for policy checks.
- Check whether setup/onboarding writes are atomic:
  - If an app creates a parent row and then a membership/owner row in two client calls, a partial failure can leave an orphaned or half-usable setup state.
  - Prefer one RPC/database function that creates the parent and membership in one transactional execution path.
  - Consider removing direct client insert policies when setup must go through the RPC.
- Check cross-tenant integrity, not just RLS predicates:
  - Independent FKs such as `booking.establishment_id` plus `booking.room_unit_id` do not prove the room belongs to that establishment.
  - Add composite uniqueness such as `(id, establishment_id)` on referenced tables and composite FKs from dependent rows.
  - Apply the same pattern to optional references like guest IDs and availability blocks.
- Check evidence language:
  - Typecheck/web export passing does not verify live RLS behavior.
  - If `supabase db lint --local` is blocked by missing Docker/local DB, record it as blocked and keep live Supabase verification explicit.

## Verdict guidance

Treat recursive RLS risks, non-atomic setup ownership creation, and cross-establishment FK gaps as blockers for a setup-foundation story unless they are out of scope and explicitly deferred with a safe interim constraint.
