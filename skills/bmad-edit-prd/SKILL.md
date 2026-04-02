---
name: bmad-edit-prd
description: Revise an existing PRD in a disciplined, contract-backed way based on validation findings or clarified product decisions.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, prd, editing, planning]
    related_skills: [bmad-create-prd, bmad-validate-prd]
---

# BMad Edit PRD

## When to Use
Use when a PRD already exists and needs targeted revision rather than a fresh rewrite.

## Goal
Update the PRD while preserving structure, traceability, and auditability.

## Procedure
1. Read the current PRD and any validation findings.
2. Identify exactly which sections need revision.
3. Use the BMad artifact tool layer to update the PRD structurally.
4. Re-validate after edits.
5. Route back to `bmad-validate-prd` if quality confirmation is still needed.

## Completion Output
Report what changed, why it changed, and whether the PRD is ready for re-validation or downstream planning.
