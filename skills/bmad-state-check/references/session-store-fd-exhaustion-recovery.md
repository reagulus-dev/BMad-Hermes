# Session-store FD exhaustion recovery pattern

Use when a user reports a previous gateway/agent session died with an error like:

```text
OSError: [Errno 24] Too many open files: '<home>/.hermes/sessions/.sessions_*.tmp'
```

## Interpretation

- This usually means the already-running agent/gateway process exhausted its per-process file descriptor limit while attempting an atomic session-store write.
- Slash commands such as `/reset` or `/new` may also fail because they still run inside the same FD-exhausted process and may need to open/update session files.
- A reboot or service restart clears the open FDs, but it does not prove the interrupted work was complete.

## Read-only recovery checklist

1. Confirm current boot/service state and FD health:
   - `uptime -s`
   - `ulimit -n`
   - inspect current gateway/agent process FD counts under `/proc/<pid>/fd` when relevant.
2. Check for stale temp files in session stores:
   - `~/.hermes/sessions/.sessions_*.tmp`
   - other active agent session stores such as `~/.openclaw/agents/<agent>/sessions/` when applicable.
3. Validate session-store readability before trusting history:
   - parse `~/.hermes/sessions/*.json` if Hermes session JSON is involved.
   - parse active agent `*.jsonl` session files if the platform uses JSONL session stores.
4. Distinguish direct cause from nearby noise:
   - stale/broken systemd services, missing install paths, and restart spam can be relevant operational cleanup, but do not automatically explain an FD exhaustion unless their process had high FD usage.
5. Resume the project from repository truth, not from the interrupted chat alone:
   - inspect `_bmad/state.json`, `_bmad/sprint-status.yaml`, `CONTINUE-HERE.md`, git status, recent commits, and dirty diffs.
   - if dirty changes exist after the reboot, treat them as interrupted work and continue the current BMad workflow rather than advancing gates.

## Reporting guidance

Keep the report separated into:

- platform/process finding: what likely happened to the agent/gateway session.
- persistence finding: whether session files/temp files look corrupt or clean.
- project-state finding: current BMad workflow/story/blockers and dirty repo state.
- next valid workflow: usually the interrupted correction/review gate, not a new story.

Do not encode a permanent rule that a specific tool or gateway is broken; capture only the recovery pattern and the checks that distinguish transient FD exhaustion from durable configuration problems.
