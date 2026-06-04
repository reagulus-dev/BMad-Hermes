# Bounded Correction Delegation for Weaker Models

Use this reference when asking a cheaper/weaker subagent model (for example MiniMax M2.7) to run `bmad-dev-story` correction work after a review blocker.

## Problem Pattern

A vague instruction such as:

> Run `bmad-dev-story` correction for STORY_ID.

can be misread by weaker models as a request to perform or summarize `bmad-code-review`. The agent may report a review verdict and never implement the correction.

## Required Brief Shape

Give the subagent a bounded implementation contract, not a broad workflow name:

1. Name the exact project root and story artifact path.
2. Say explicitly: **this is implementation/correction work, not code review**.
3. Quote the blocker(s) and acceptance criteria that must be corrected.
4. List the exact files or code areas to inspect first.
5. Define allowed scope and explicit out-of-scope items.
6. Require code changes only if needed to close the blocker; otherwise require evidence-backed explanation.
7. Require validation commands and exact evidence to append to the story artifact.
8. Require state/sprint/continuation synchronization only after implementation validation passes.
9. Prohibit declaring PASS/BLOCKED review verdicts; those belong to `bmad-code-review` after correction.
10. Ask for a concise handoff: changed files, commands run, evidence anchor, remaining unverified items.

## Minimal Prompt Skeleton

```text
You are running `bmad-dev-story` correction for STORY_ID in PROJECT_ROOT.
This is implementation/correction work, NOT `bmad-code-review`.
Do not issue a review verdict. Your job is to fix the listed blocker(s), validate, and update the story's Dev Agent Record/evidence.

Inputs:
- Story artifact: PATH
- Review blocker(s): QUOTED_BLOCKERS
- Required acceptance criteria: QUOTED_AC
- Prior evidence anchor: ANCHOR

Bounded task:
1. Inspect only these relevant files first: FILES.
2. Implement the smallest correction that closes the blocker(s).
3. Preserve out-of-scope boundaries: OUT_OF_SCOPE.
4. Run: VALIDATION_COMMANDS.
5. Append evidence to the story artifact under a correction/dev-agent section.
6. Update `_bmad/state.json`, `_bmad/sprint-status.yaml`, and `CONTINUE-HERE.md` only to reflect implemented-not-reviewed correction status.

Do not run or claim `bmad-code-review`; after your correction, the next workflow is `bmad-code-review for STORY_ID`.
```

## Verification Expectations for Parent Agent

After the subagent returns, the parent/orchestrator should verify:

- The subagent made implementation or artifact correction changes, not just prose review.
- The story artifact contains a correction/dev-agent evidence section, not a fresh review verdict.
- State says correction implemented / needs review, not review passed, unless a separate authorized review actually ran.
- Validation commands were really run or explicitly marked unrun.
