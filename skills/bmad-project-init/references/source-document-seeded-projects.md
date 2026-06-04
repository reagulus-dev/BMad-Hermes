# Source-Document-Seeded BMad Project Initialization

Use this reference when a new BMad project is created from an uploaded PDF/spec/brief and the user asks for product brief, PRD, architecture, or similar planning artifacts.

## Pattern

1. Create the project root and canonical `_bmad/` tree.
2. Preserve the original source document under `docs/source/` instead of only reading it from Hermes cache.
3. Extract text and metadata next to the source file, e.g.:
   - `docs/source/<name>.extracted.txt`
   - `docs/source/<name>.metadata.json`
4. Generate planning artifacts from the extracted text into the canonical artifact location.
5. Mark generated artifacts as source-derived drafts, not founder-approved truth.
6. Update `_bmad/state.json` with `current_phase: planning`, generated artifact paths, and next recommended workflows.
7. Add a compact `CONTINUE-HERE.md` with source paths, artifact paths, product boundary notes, and open decisions.

## Good defaults

- Planning artifact paths:
  - `_bmad/artifacts/planning/product_brief.md`
  - `_bmad/artifacts/planning/prd.md`
  - `_bmad/artifacts/planning/architecture.md`
- State trust level: `partial` until validated with founder or downstream BMad validation.
- Next workflows after initial conversion:
  - `bmad-validate-prd`
  - `bmad-create-ux-design`
  - `bmad-create-epics-and-stories`

## Safety / boundary handling

When source material describes powerful or dual-use automation, preserve the legitimate product intent while explicitly writing product boundaries into the brief/PRD/architecture. Examples:

- authorized workflows only
- human-in-the-loop verification/approval
- no request flooding
- no unauthorized access
- no CAPTCHA/anti-bot bypass
- no fully automated payment/checkout behavior

## Verification

Before reporting completion, verify:

- source document exists under `docs/source/`
- extracted text/metadata exist and include page/character counts where available
- planning artifacts exist and are non-empty
- `_bmad/state.json` references the artifacts and the correct project root
- `CONTINUE-HERE.md` exists with concise next-step guidance
