# Continue Here: BMad Workflow Plugin

Project root:
- `/home/reagulus/projects/bmad-workflow-plugin`

> Rename completed 2026-04-02: all `alice-*`/`alice_*` names replaced with `bmad-*`/`bmad_*`
> throughout Python package, skills, workflow registry, MCP server, and config.yaml.
> Hermes tools now visible as `mcp_bmad_*`. Current repo baseline after the latest
> state-migration pass: 95/95 tests passing.

Project root:
- `/home/reagulus/projects/bmad-workflow-plugin`

Durable design references:
- `~/.hermes/skills/software-development/bmad-operating-model/references/plugin-implementation-layout.md`
- `~/.hermes/skills/software-development/bmad-operating-model/references/plugin-starter-skeleton.md`

---

## What was built (P13 batch — 2026-04-02)

### Canonical module layout ✓
Canonical Alice skills patched and saved:
- bmad-artifact-policy, bmad-state-migration, bmad-code-review,
  bmad-correct-course, bmad-dev-story, bmad-evidence-reporting,
  bmad-operating-model, bmad-project-init, bmad-qa-gate, bmad-state-check

### Phase 1–3 artifact contracts ✓
`registry/artifact_contracts.yaml` now defines contracts for all 9 Phase 1–3 artifacts:
- Phase 1 (analysis): `brainstorming_session`, `product_brief`, `prfaq`
- Phase 2 (planning): `prd`, `prd_validation_report`, `ux_design`
- Phase 3 (solutioning): `architecture`, `epics_and_stories`, `project_context`

Each contract specifies: path resolution rules (preferred + legacy_compatible),
source templates, field definitions, required/optional sections, and workflow permissions.

### Templates ✓
All Phase 1–3 templates created under `templates/`:
`brainstorming-session.md`, `product-brief.md`, `prfaq.md`, `prd.md`,
`prd-validation-report.md`, `ux-design.md`, `architecture.md`,
`epics-and-stories.md`, `project-context.md`

### Schema models ✓
`schemas/artifact_models.py` now has dataclass models for all Phase 1–3 artifacts
plus Phase 4 (`review_record`, `qa_record`). `schemas/common.py` `ArtifactType`
enum expanded to cover all artifact types.

### Parsers ✓
All Phase 1–3 parsers created under `parsers/`:
`brainstorming_session_parser.py`, `product_brief_parser.py`, `prfaq_parser.py`,
`prd_parser.py`, `prd_validation_report_parser.py`, `ux_design_parser.py`,
`architecture_parser.py`, `epics_and_stories_parser.py`, `project_context_parser.py`
All reuse `MarkdownSectionsParser` as the section-extraction engine.

### Validators ✓
All Phase 1–3 validators created under `validators/`:
`brainstorming_session_validator.py`, `product_brief_validator.py`,
`prfaq_validator.py`, `prd_validator.py`, `prd_validation_report_validator.py`,
`ux_design_validator.py`, `architecture_validator.py`,
`epics_and_stories_validator.py`, `project_context_validator.py`
Plus a shared `validators/common.py` with `ValidationHelpers` to reduce repetition.

### Mutators ✓
All Phase 1–3 mutators created under `mutations/`:
`brainstorming_session_mutator.py`, `product_brief_mutator.py`,
`prfaq_mutator.py`, `prd_mutator.py`, `prd_validation_report_mutator.py`,
`ux_design_mutator.py`, `architecture_mutator.py`,
`epics_and_stories_mutator.py`, `project_context_mutator.py`
All reuse a shared `_rebuild_markdown()` helper from `brainstorming_session_mutator.py`.

### ArtifactService wiring ✓
`services/artifact_service.py` now instantiates and dispatches all Phase 1–3
parsers, validators, and mutators alongside the existing Phase 4 ones.
The `_parsers`, `_validators`, and `_mutators` dicts are now complete.

### Workflow registry ✓
`registry/workflow_registry.yaml` already had all Phase 1–3 workflow entries.
No changes were needed.

### Test suite baseline ✓ (2026-04-02, session 2)
- 4 test files had raw markdown embedded without triple-quote wrappers (syntax errors
  from a previous session cut-off). Fixed: test_story_parser.py,
  test_story_validator.py, test_sprint_status_parser.py,
  test_sprint_status_validator.py
- pyproject.toml lacked proper package discovery; editable install now works
- 2 pre-existing test failures fixed:
  - PathResolver: ambiguous = True now fires whenever >1 location has the file
    (not only when preferred is absent)
  - TemplateRenderer: added {{{{ / }}}} escape sequences for literal {{ / }}
- Project renamed to `bmad-workflow-plugin`; current reliable test command is:
  `cd /home/reagulus/projects/bmad-workflow-plugin && .venv/bin/pytest tests/ -v`
- All 61 tests pass.

### Registry recovery note ✓
- `bmad_workflow_plugin/registry/workflow_registry.yaml` was accidentally corrupted on disk
  by a dedup-placeholder write during a read/modify/write flow.
- It was restored from the original `write_file` payload embedded in Hermes session logs
  (`~/.hermes/sessions/session_20260402_020851_8f46e7.json`).
- After restoration, tests still pass 61/61.

---

## Audit: Plugin + Skills vs Hermes/BMad Integration (2026-04-02)

### How Hermes registers tools (important)
Hermes has two extension mechanisms:
1. **Native MCP server** — configure under `mcp_servers:` in `~/.hermes/config.yaml`.
   Hermes connects via stdio at startup, discovers tools via MCP protocol, registers them
   into the tool registry automatically. No Hermes source changes needed.
   This is the correct integration path for the bmad-workflow-plugin.
2. **Direct tool file registration** — tool files in `~/.hermes/hermes-agent/tools/`
   call `registry.register()` at import time. Requires modifying Hermes source.
   Not suitable for a user-space plugin.

The `plugin.py` currently exports `register_plugin(api)` but the `api` param is ignored
and there is no MCP server, no pyproject.toml entry_points, and no config.yaml entry.
The tools work as a Python library but are not callable by Hermes at all in current form.

### What BMad actually is (from source audit of github.com/bmad-code-org/BMAD-METHOD)
BMad is a multi-agent, multi-phase workflow method distributed as markdown skill files
installed into AI coding tools. Core concepts:
- Specialized agents: Analyst/Mary, PM/John, Architect/Winston, Scrum Master/Bob,
  Dev/Amelia, QA/Quinn, UX/Sally, Tech Writer/Paige
- 4-phase pipeline: Analysis → Planning → Solutioning → Implementation
- Each phase produces template-backed artifacts that become context for the next
- Project config lives in `_bmad/core/config.yaml`
  (project_name, output_folder, communication_language, user_name, etc.)
- Artifacts go to `{output_folder}/` (default: `_bmad-output/`)
- Implementation tracking via `sprint-status.yaml`
- Workflow files reference multi-step instructions in `./steps/step-NN-*.md` files

### What is working well
1. WorkflowRouter — state-regime gates, sprint-status parsing, story-status-triggered
   routing, RoutingDecision dataclass. This is the strongest part.
2. Tool surface API — 9 tools are well-named and mechanically sound.
   Contract-in / contract-out design is correct.
3. Artifact contracts + templates — artifact_contracts.yaml + templates/ pattern
   is correct for the goal. Contracts as enforced schema is the right approach.
4. Test suite — 61/61 passing.
5. Alice policy skills — bmad-operating-model, bmad-dev-story, bmad-project-init,
   bmad-code-review, bmad-evidence-reporting, bmad-qa-gate are solid policy docs.
   Philosophy is correctly placed: doctrine in skills, mechanics in tools.

### Critical gaps (blockers for actual Hermes integration)

**Gap 1: No Hermes plugin registration mechanism** [DONE 2026-04-02]
`bmad_workflow_plugin/mcp_server.py` added — FastMCP stdio server exposing all 9 tools.
`~/.hermes/config.yaml` updated with `mcp_servers.bmad` entry.
On Hermes restart, tools appear as `mcp_bmad_get_state`, `mcp_bmad_next_workflow`, etc.
Smoke tested: all 3 core tools (get_state, next_workflow, workflow_help) respond correctly.

**Gap 2: Phase 1-3 BMad skill files don't exist** [CRITICAL]
`workflow_registry.yaml` references skills: `bmad-brainstorming`, `bmad-product-brief`,
`bmad-prfaq`, `bmad-create-prd`, `bmad-validate-prd`, `bmad-create-ux-design`,
`bmad-create-architecture`, `bmad-create-epics-and-stories`,
`bmad-check-implementation-readiness`. None exist in `~/.hermes/skills/`.
When `bmad_next_workflow` returns one of these, the agent gets a skill name pointing
at nothing. This is item 1 in the original "What's still left" list.
FIX: Create Hermes skill wrappers for each, porting BMad workflow docs into Hermes
SKILL.md format with the upstream workflow steps included.

**Gap 3: Path convention mismatch with BMad upstream** [DONE 2026-04-02]
Implemented a BMad compatibility shim for both config and artifact path resolution.

What changed:
- Added `state/bmad_config.py` with `BmadConfigReader` for `_bmad/core/config.yaml`
- `StateReader` now treats config-only BMad projects as `legacy_only` state instead of `missing`
- `StateReader` injects `__bmad_config__` into loaded state for downstream normalization
- `StateNormalizer` now exposes BMad config fields under `normalized_state['bmad_config']`
- `PathResolver` now honors configurable `output_folder` from `_bmad/core/config.yaml`
- `PathResolver` can resolve legacy artifact paths under custom output roots, not just `_bmad-output/`
- `PathResolver` now enriches missing `project_name` from BMad config when building paths
- `PathResolver` now uses wildcard/glob fallback for unresolved placeholders so config-driven
  project artifacts can still be found without explicit identity args when the match is unique
- `ArtifactService.create_from_template()` now passes full `template_vars` as path identity
  instead of only `story_key`

Coverage added:
- `tests/test_bmad_config_compatibility.py`
  - config-only project => `legacy_only`
  - `project_name` inferred from config for preferred path building
  - custom `output_folder` respected for legacy sprint-status resolution
  - legacy project artifact resolution works without explicit identity when unique

Current test baseline after Gap 3: 65/65 passing.

### Significant issues (not blockers but need addressing)

**Issue 1: Duplicate workflow naming / alias confusion** [RESOLVED 2026-04-02]
Canonical workflow IDs remain `bmad-*`, and compatibility aliases now cover the
unprefixed names used by older routing/tests/docs (`project-init`, `state-check`,
`state-migration`, `sprint-planning`, `create-story`, `dev-story`, `code-review`,
`qa-gate`, `retrospective`, `correct-course-impl`).

Also fixed a deeper issue: `WorkflowRouter` had hardcoded `bmad-operating-model`
for `sprint-planning`, `create-story`, and `retrospective`, so YAML changes alone
would not have corrected runtime behavior.

**Issue 2: bmad-project-init hardcoded path** [MEDIUM]
The skill text says: "Confirm the target project root is under `/home/reagulus/projects/`"
This is a personal path. It will break for any other user or environment.
FIX: Make the constraint configurable or remove it entirely from the skill.

**Issue 3: No bmad_init_project tool** [RESOLVED 2026-04-02]
Added a mechanical `bmad_init_project` tool backed by `services/init_service.py`.

What it now does:
- creates canonical `_bmad/` scaffold directories
- writes `_bmad/state.json` from the canonical template when missing
- writes `_bmad/notes.md` when missing
- writes `_bmad/core/config.yaml` when enabled and missing
- creates the configured legacy-compatible output root (default `_bmad-output`)
- preserves existing meaningful files instead of overwriting them blindly
- reports created vs preserved paths explicitly

Wiring added:
- schema: `schemas/bmad_init_project.py`
- tool: `tools/bmad_init_project.py`
- plugin registration: `plugin.py`
- MCP exposure: `mcp_server.py`

Coverage added:
- scaffold creation
- preservation of existing `state.json` and `config.yaml`
- tool registration / success path

Current test baseline after init-tool implementation: 72/72 passing.

**Issue 4: Workflow entries pointing at bmad-operating-model as recommended_skill** [RESOLVED 2026-04-02]
Created dedicated workflow skills:
- `bmad-sprint-planning`
- `bmad-create-story`
- `bmad-retrospective`

Updated both `workflow_registry.yaml` and `WorkflowRouter` so runtime routing now
lands on those workflow skills rather than the doctrine-only `bmad-operating-model`.

Coverage added:
- registry alias resolution tests
- no-sprint-status => `bmad-sprint-planning`
- done story with next backlog story => `bmad-create-story`
- done epic with optional retrospective => `bmad-retrospective`

Current test baseline after routing fix: 69/69 passing.

**Issue 5: ArtifactService eager-loads all 25+ parsers/validators/mutators** [RESOLVED 2026-04-02]
`ArtifactService` now lazy-loads parsers, validators, and mutators per artifact type on first use
via factory maps and per-type caches.

What changed:
- eager per-service instantiation was removed from `services/artifact_service.py`
- parser/validator/mutator dispatch now goes through on-demand factory lookup
- instantiated components are cached after first use so repeated calls reuse the same object
- the service can also accept injected factory maps in tests to verify behavior directly

Coverage added:
- `tests/test_artifact_service_lazy_loading.py`
  - confirms no parser/validator/mutator factory runs during `ArtifactService()` construction
  - confirms `read_artifact()` instantiates only the parser/validator needed for that artifact type
  - confirms repeated reads reuse cached components
  - confirms `update_artifact_sections()` instantiates the mutator only when mutation is invoked

**Issue 6: WorkflowRegistryLoader reloads YAML on every call** [RESOLVED — docs were stale]
This note was true in an earlier audit draft but is no longer true in the current code.
`bmad_workflow_plugin/registry/workflow_loader.py` now caches the parsed registry in
`self._registry` and returns it on subsequent `load()` calls.

Current reality:
- YAML is parsed once per `WorkflowRegistryLoader` instance
- `raw_registry` also reuses the cached payload via `self._raw`
- there is not yet an explicit reload/invalidate method, but the repeated re-parse issue
  described here is already fixed for normal runtime usage

---

## What's still left (updated)

1. **[DONE] Hermes MCP server registration** — `mcp_server.py` (FastMCP) written,
   `~/.hermes/config.yaml` updated to `mcp_servers.bmad`. Restart Hermes to activate.

2. **[DONE 2026-04-02] Skill SKILL.md files for Phase 1–3 BMad workflows** — Hermes-native SKILL.md wrappers created for:
   `bmad-brainstorming`, `bmad-product-brief`, `bmad-prfaq`, `bmad-create-prd`,
   `bmad-validate-prd`, `bmad-create-ux-design`, `bmad-create-architecture`,
   `bmad-create-epics-and-stories`, `bmad-check-implementation-readiness`.
   Also added `bmad-generate-project-context` because it is a real upstream Phase 3 workflow
   and was also missing locally.

   Follow-up completed 2026-04-02: the remaining registry-referenced upstream workflow
   skills outside the core implementation slice were added as Hermes-native wrapper skills,
   so the registry no longer points at missing skill names.

3. **[DONE 2026-04-02] BMad path/config compatibility** — `_bmad/core/config.yaml`
   is now recognized, config fields are surfaced in normalized state, and PathResolver
   can resolve BMad-native artifacts under configurable `output_folder` roots.

   Gap 4 is effectively addressed through this implementation choice: the upstream
   BMad config fields (`project_name`, `output_folder`, `user_name`,
   `communication_language`, `document_output_language`, `user_skill_level`) now
   live in the first-class `_bmad/core/config.yaml` concept rather than being copied
   into top-level `state.json`. `bmad_init_project` writes the config file, the
   compatibility layer reads it, and normalized state surfaces it under
   `normalized_state['bmad_config']`.

4. **[DONE 2026-04-02] Fix workflow_registry.yaml routing holes** — added canonical
   aliases, created dedicated implementation workflow skills, and updated router
   hardcoded paths so runtime recommendations now match the registry intent.

5. **[DONE 2026-04-02] Add bmad_init_project tool** — mechanical `_bmad/` scaffold
   creation is now implemented and exposed through the plugin/MCP server.

6. **[DONE 2026-04-02] Fix bmad-project-init skill** — removed the hardcoded
   `/home/reagulus/projects/` assumption so the skill now operates on the confirmed
   target project root without personal-path coupling.

7. **Integration tests** — MCP-server-level coverage added 2026-04-02.

Added `tests/test_mcp_server_integration.py` covering:
- FastMCP tool registration (`mcp._tool_manager.list_tools()`)
- stdio initialize handshake using the real launch pattern (`uv run --project ... python -m bmad_workflow_plugin.mcp_server`)
- direct MCP-exposed round-trip for `bmad_init_project` + `bmad_get_state`
- alias-aware `bmad_workflow_help` coverage after routing/registry fixes

Current test baseline after MCP integration coverage: 76/76 passing.

Phase 1–3 artifact service end-to-end coverage added 2026-04-02.

Added `tests/test_phase123_artifact_service_e2e.py` covering:
- contract-backed creation across all 9 Phase 1–3 artifact types
- read/validate/update round-trips through `ArtifactService`
- contract-path destination assertions for planning and solutioning artifacts

This coverage exposed and drove real parser fixes:
- `ProductBriefParser` now canonicalizes `The Problem`/`The Solution`/`What Makes This Different`
  into contract section IDs
- `ProjectContextParser` now canonicalizes `Technology Stack & Versions`,
  `Critical Implementation Rules`, and `Conventions & Patterns`
- `PRFAQParser` now synthesizes canonical `headline` and `press_release` sections from the
  real template shape and maps `The Verdict` correctly

Current test baseline after Phase 1–3 E2E coverage: 86/86 passing.

Registry/skill cleanup added 2026-04-02.

Remaining registry-referenced upstream workflow skill names were added as Hermes-native
wrapper skills, including analysis, implementation, and anytime workflows such as:
- `bmad-market-research`
- `bmad-domain-research`
- `bmad-technical-research`
- `bmad-edit-prd`
- `bmad-sprint-status`
- `bmad-quick-dev`
- `bmad-checkpoint-preview`
- `bmad-qa-generate-e2e-tests`
- `bmad-document-project`
- `bmad-agent-tech-writer`
- `bmad-party-mode`
- `bmad-help`
- `bmad-index-docs`
- `bmad-editorial-review-prose`
- `bmad-editorial-review-structure`
- `bmad-review-adversarial-general`
- `bmad-review-edge-case-hunter`
- `bmad-distillator`

The workflow registry now resolves to installed skill names throughout the current surface.

8. **[DONE 2026-04-02] Real upstream layout verification** — verified against real exported BMad-style project layouts under:
   - `/home/reagulus/projects/lapseless`
   - `/home/reagulus/projects/proofkey`
   - `/home/reagulus/projects/rotacore`
   - `/home/reagulus/projects/lantern`

   What was confirmed/fixed:
   - `BmadConfigReader` now reads both `_bmad/core/config.yaml` and the real exported `_bmad/config.yaml` layout.
   - PathResolver legacy compatibility now finds real exported planning artifacts such as:
     - `product-brief-<Project>.md` and dated variants
     - `prd.md`, `prd-<Project>.md`, `prd-vN.md`
     - `prd-validation-report.md`, `prd-validation-report-<Project>.md`, `prd-validation-report-vN.md`
     - `ux-design-specification.md`
     - `architecture.md`
     - `epics-and-stories-<Project>.md` / `epics-and-stories.md`
     - implementation stories under `_bmad-output/implementation-artifacts/stories/`
   - Added story-key enrichment so short IDs like `1-1` can resolve to exported files like
     `story-1-1-create-property-record.md`.
   - `SprintStatusParser` now handles additional real-world formats:
     - nested YAML sprint/story lists (`lapseless` style)
     - markdown-table development status docs (`proofkey` style)
     - YAML-with-markdown-appendix (`rotacore` style)
     - sprint-level `story_ids` + sprint status fallback (`lantern` style)
   - Added targeted tests for these real-layout compatibility cases.

   Current baseline after this work: `92/92` passing.

   Residual findings from real layouts:
   - `next_workflow` still correctly routes these real projects to `bmad-state-migration` first because
     they are genuinely `legacy_only` projects until normalized `_bmad/state.json` migration happens.
   - Some real exports do not contain every Phase 1–3 artifact in a canonical one-file form
     (for example `rotacore` missing clear `ux_design` / `epics_and_stories` matches).
   - Some projects contain intentionally ambiguous artifacts (for example `lantern` has both `prd.md`
     and `prd-v2.md`), so resolver ambiguity is expected and should remain explicit rather than guessed.
   - The currently running Hermes session still has the old MCP server process loaded; restart Hermes to
     pick up these source changes on the `mcp_bmad_*` tool surface.

9. **[DONE 2026-04-02] First mechanical `bmad-state-migration` implementation** —
   added an actual plugin/MCP tool surface for non-destructive legacy-state migration.

   What was added:
   - `StateMigrationService` for mechanical migration from legacy `_bmad/state.json`
     or config-only real export layouts
   - `bmad_migrate_state` plugin tool and `mcp_bmad_migrate_state` FastMCP exposure
   - timestamped pre-migration backup creation beside existing `_bmad/state.json`
   - preservation of legacy `completedWorkflows` history under `legacy_bmad.completed_workflows`
   - seeding of normalized snake_case Alice live-state fields
   - artifact-aware migration helpers that inspect real exported planning and sprint-status shapes
   - current-story inference from real sprint-status documents during migration
   - focused service/tool/MCP tests for both legacy-state and config-only export cases

   Current baseline after this work: `95/95` passing.

   Remaining limits of this pass:
   - post-migration state remains intentionally `partially_normalized` because legacy camelCase
     fields are preserved in place rather than destructively removed
   - `next_workflow` will still recommend `bmad-state-check` immediately after migration,
     which is the intended conservative handoff
   - ambiguous exported artifacts (for example `prd.md` + `prd-v2.md`) remain explicit blockers
     rather than being auto-resolved

10. **TemplateRenderer variable expansion verification** — covered by existing tests.

11. **[DONE 2026-04-02] MCP install/run docs tightened** — `README.md` now reflects the
    operational plugin rather than the old scaffold and documents:
    - `uv pip install -e .` as the preferred editable install path
    - the exact `uv run --project ... python -m bmad_workflow_plugin.mcp_server` launch shape
    - Hermes `mcp_servers.bmad` config
    - a recommended live verification sequence for `mcp_bmad_bmad_*` tools
    - common MCP startup / stale-session pitfalls

12. **[DONE 2026-04-02] Live MCP smoke verification against stowsy** — verified the
    currently loaded `mcp_bmad_*` tool surface against `/home/reagulus/projects/stowsy`.

    What was confirmed live:
    - `mcp_bmad_get_state` is available in the current Hermes session and correctly reports
      `stowsy` as `legacy_only` before migration.
    - normalized output already surfaces real `_bmad/config.yaml` data under
      `normalized_state.bmad_config`:
      - `project_name: Stowsy`
      - `output_folder: _bmad-output`
      - `communication_language: english`
      - `document_output_language: english`
      - `user_skill_level: expert`
    - `mcp_bmad_migrate_state` is present live and successfully migrated the real legacy
      `_bmad/state.json` for `stowsy`.
    - migration created a timestamped backup beside state:
      `/home/reagulus/projects/stowsy/_bmad/state.pre-alice-backup-2026-04-02T132427Z.json`
    - migration preserved `197` legacy workflow history entries and added normalized
      Alice live-state keys in place.
    - post-migration `mcp_bmad_get_state` reports `partially_normalized` with
      `next_recommended_workflows = ["bmad-state-check"]`.
    - post-migration `mcp_bmad_next_workflow` conservatively routes to
      `bmad-state-check` with reason: `State is only partially normalized.`

    Important reality update:
    - the previously noted "current Hermes session still has the old MCP server process loaded"
      warning no longer applied in the session used for this verification; the live tool surface
      already included `mcp_bmad_migrate_state` and exercised the updated code successfully.

---

## If resuming in a fresh session

1. Read this file.
2. Read the two reference docs in `bmad-operating-model/references/`.
3. Inspect the scaffold under `/home/reagulus/projects/bmad-workflow-plugin`.
4. Run `cd /home/reagulus/projects/bmad-workflow-plugin && .venv/bin/pytest tests/ -v`
   to confirm baseline is still 95/95.
5. Restart Hermes so `mcp_servers.bmad` is loaded.
6. Verify MCP server independently if needed:
   - `cd /home/reagulus/projects/bmad-workflow-plugin`
   - `echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0"}}}' | .venv/bin/python -m bmad_workflow_plugin.mcp_server`
   - expected: JSON response with `serverInfo.name` = `bmad`
7. In Hermes, confirm a system message says the `bmad` server was added and that
   tools like `mcp_bmad_get_state` are available.
8. Check which item in "What's still left" was last worked on.
9. Continue from there.

Current active item: Decide the next post-polish improvement now that plugin container narrowing, ArtifactService, WorkflowRouter, WorkflowService, and workflow-help wrapper tightening are done.
Previous active item: DONE — BmadWorkflowPlugin lazy service/tool container plus MCP get_tool path for one-tool-at-a-time resolution.
Previous active item: DONE — WorkflowService lazy router construction and workflow-help wrapper reuse of that service.
Previous active item: DONE — WorkflowRouter lazy-loading for state/path/parser components where needed.
Previous active item: DONE — ArtifactService lazy-loading for parsers/validators/mutators.
Previous active item: DONE — MCP install/run documentation tightening in README.
Previous active item: DONE — live MCP reload / smoke verification against `stowsy`, including confirmation that `mcp_bmad_migrate_state` is present and works on a real project.
Previous active item: DONE — first mechanical `bmad-state-migration` implementation.
Previous active item: DONE — real upstream layout verification against actual exported BMad-style projects.
Previous active item: DONE — broader Phase 1–3 artifact service E2E coverage.
Previous active item: DONE — registry cleanup for remaining missing upstream workflow skills.

## Next Session / After Restart

Primary next task:
- choose the next highest-value improvement now that the lazy-loading/doc reconciliation pass is green

Suggested follow-up sequence:
1. Reconfirm baseline:
   - `cd /home/reagulus/projects/bmad-workflow-plugin && .venv/bin/pytest tests/ -v`
   - expected after lazy-loading/doc pass: 100/100 passing
2. Nice follow-up if desired:
   - inspect whether `bmad-state-migration` should infer richer blockers/evidence from review/QA artifacts on real exported projects
   - decide whether ambiguous multi-PRD exports (for example `prd.md` + `prd-v2.md`) need extra tooling beyond the current explicit ambiguity signal