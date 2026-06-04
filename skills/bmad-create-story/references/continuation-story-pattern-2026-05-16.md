# Continuation Story Pattern (e.g., HLX-3.3b)

Context:
- HLX-3.3 (Task Groups) was review-passed with notes.
- DB migration and repository were in place; UI was wired to an in-memory array.
- Next planned story (HLX-3.4) was for Routes, not Task Groups wiring.

Decision:
- Do NOT repurpose HLX-3.4 to absorb HLX-3.3’s open wiring.
- Create HLX-3.3b: a small, focused continuation story to:
  - Wire Task Groups UI to DB via preload/IPC.
  - Verify migration 004_task_groups in runtime.
  - Add any missing tests/evidence.

Rules:
- Use a continuation story (e.g., HLX-3.3b) when:
  - A story is review_passed_with_notes but has concrete open gaps.
  - The gaps are:
    - DB wiring for existing UI.
    - Migration runtime verification.
    - Missing IPC, tests, or evidence.
- Keep continuation scope tight:
  - Only what is needed to close the gaps.
  - Do not broaden into the next epics_and_stories story.
- Keep epics_and_stories.md alignment:
  - The next story (e.g., HLX-3.4) must still match its planned scope.
  - The continuation story is an add-on, not a replacement.
