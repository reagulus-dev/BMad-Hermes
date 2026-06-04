# CardForge CF-E1-S3 — Next Build Zero-Output / Next.js Compiled-but-Silent

**Date:** 2026-05-24
**Story:** CF-E1-S3 (Inventory and Lots Module)
**Pattern:** Next.js `next build` returning zero stdout despite successful compilation

## Symptom

`./node_modules/.bin/next build` exits 0 but produces zero lines of output — not an error, not a success message, just silence. The build actually succeeds (routes compiled, bundles visible in a second run with `| tail -20`).

## Confirmed Root Cause

Terminal backend capturing only the first line of multiline output from the background PTY. The `next build` command writes its progress bar / status lines to the same PTY stdout as the final summary, but the backend captures only the first line.

**Not a Next.js failure. Not a Hermes failure. Expected PTY behavior when progress bars and final summary share stdout.**

## When This Pattern Appears

- Any Next.js build/run command that uses TTY-aware progress bars (build, dev, lint --fix)
- Any command that writes multiple lines to PTY stdout and exits 0

## Workaround

Always pipe output to `tail` (or `grep`) to force line-buffered capture:

```bash
./node_modules/.bin/next build 2>&1 | tail -20   # always shows last lines
./node_modules/.bin/next build 2>&1 | grep -E "(Error|error|Failed|✓|compiled)" | head -30
```

The `tail -20` approach is the reliable pattern for confirming build success.

## Related

- Next.js progress bars / TTY detection: uses `should-indent` to decide whether to emit ANSI progress or full lines
- The zero-output issue does NOT indicate build failure — exit code 0 means success
- A second invocation immediately after (no cache invalidation) also returns zero output, confirming PTY capture issue

## Tags

`cardforge` `nextjs` `build` `pty` `terminal-backend` `zero-output`