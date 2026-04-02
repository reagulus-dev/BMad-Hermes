---
name: bmad-qa-generate-e2e-tests
description: Generate automated E2E or API-oriented test coverage for implemented behavior without confusing test generation with full QA sign-off.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, qa, e2e, testing]
    related_skills: [bmad-qa-gate, bmad-dev-story, test-driven-development]
---

# BMad QA Generate E2E Tests

## When to Use
Use when implemented behavior needs automated regression coverage, especially before or alongside QA review.

## Goal
Expand automated confidence while keeping the distinction between generated tests and actual QA conclusions explicit.

## Procedure
1. Identify the implemented flows worth automating.
2. Generate focused E2E/API tests tied to the story scope.
3. Run them and report pass/fail honestly.
4. Note what remains unverified manually.
5. Hand off to `bmad-qa-gate` for actual QA judgment if needed.

## Completion Output
Report what tests were added, what they cover, run results, and remaining QA gaps.
