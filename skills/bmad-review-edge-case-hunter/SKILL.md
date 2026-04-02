---
name: bmad-review-edge-case-hunter
description: Review a proposal or implementation with explicit focus on edge cases, unusual states, and failure boundaries that normal review may overlook.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, review, edge-cases, quality]
    related_skills: [bmad-review-adversarial-general, bmad-qa-gate, systematic-debugging]
---

# BMad Edge Case Hunter Review

## When to Use
Use when correctness depends on handling non-happy-path conditions and unusual transitions.

## Goal
Surface edge conditions that should influence design, implementation, QA, or release confidence.

## Procedure
1. Identify the main flows and assumptions.
2. Enumerate boundary cases, invalid states, timing races, and odd inputs.
3. Evaluate whether the current artifact/work addresses them.
4. Separate true risks from hypothetical noise.
5. Route substantive findings back into the relevant BMad workflow.

## Completion Output
Report the highest-value edge cases found and the recommended remediation path.
