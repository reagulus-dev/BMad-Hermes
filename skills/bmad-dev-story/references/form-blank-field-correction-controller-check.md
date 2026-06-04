# Form blank-field correction controller check

Use this when a BMad dev-story correction touches form actions that coerce optional fields, especially after a weaker-model/MiniMax correction.

## Durable lesson

A blocker may involve preserving blank-string intent for **edit** submissions while leaving **create** semantics unchanged. Do not blindly apply the same `FormData` coercion change to both paths.

Concrete CardForge CF-E1-S5 pattern:
- Edit bug: `formData.get("vendor")?.toString() || undefined` collapsed `""` to `undefined`, so an existing optional field could not be cleared; Prisma received `undefined` and left the value unchanged.
- Correct edit shape: preserve `""` through validation, then map `""` to `null` at the update boundary.
- Create-path guard: blank optional create fields should usually stay `null`/absent, not persist as empty strings. If the correction removes `|| undefined` from create as well, verify the schema/action still maps blanks to `null` before repository writes.

## Controller acceptance checklist

After a delegated correction:
1. Inspect both create and update actions, not only the blocked update path.
2. Add or verify focused tests for:
   - blank edit field clears existing value (`null`, not `undefined`);
   - non-blank edit value persists unchanged;
   - blank create optional field does not persist an unwanted empty string.
3. If the subagent fixed the main blocker but broadened the edit-path change into create-path behavior, patch the create path or add a regression test before reconciling BMad artifacts.
4. In the Dev Agent Record, distinguish subagent work from controller tightening when applicable.
