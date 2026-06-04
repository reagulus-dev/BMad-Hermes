---
name: bmad-quick-dev
description: Run a compressed BMad delivery loop when the task is small enough for a short requirements-to-implementation cycle without abandoning evidence and review discipline.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, quick-dev, implementation]
    related_skills: [bmad-state-check, bmad-dev-story, bmad-code-review]
---

# BMad Quick Dev

## When to Use
Use for small bounded work where a full long-form artifact chain would be excessive but disciplined execution is still needed.

## Goal
Preserve BMad truthfulness and verification while compressing the cycle.

## Procedure
1. Clarify the concrete outcome and constraints.
2. Check current state and whether a story/artifact anchor already exists.
3. Implement the bounded change with validation.
4. If the slice is scaffolding/foundation-only, keep UI copy, routing, and status text strictly aligned with what is actually landed. Do not present setup previews or future runtime paths as working features yet.
5. Review and summarize evidence honestly.
6. Route to fuller BMad workflows if the scope grows.

## Pitfalls
- Do not let scaffold-only work sound like a shipped feature. If download/runtime/device verification is not landed, say so explicitly in the UI copy and final report.
- If gating logic blocks a path (for example storage or device support), ensure the headline/reason text does not still sound positive or available.
- Update continuation/state artifacts so the next session knows whether the slice is source-verified only, build-verified, or runtime-verified.

## Completion Output
Report scope, evidence, limits of confidence, and next action if more formal workflow is needed.
