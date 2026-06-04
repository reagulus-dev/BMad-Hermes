# Search/Tool Loop Avoidance Pattern

Trigger:
- You are repeatedly calling the same search/grep/scan command with identical arguments and getting the same result or same error.
- You are stuck in a long chain of identical tool calls with no new information.

Fix:
- Stop repeating the same call.
- Try:
  - Different pattern or scope (e.g., content vs files, subdirectory, file_glob).
  - A terminal command (e.g., find, ls, head) to inspect structure.
  - Falling back on known paths, prior session context, or artifacts.
- If still stuck:
  - Proceed the best you can with existing information.
  - Call out what is unknown and why in your review/response.

Rationale:
- Prevents wasting tokens/time on infinite loops.
- Keeps reviews and tasks moving forward even when a tool behaves oddly.
