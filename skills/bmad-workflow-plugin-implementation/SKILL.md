---
name: bmad-workflow-plugin-implementation
description: Implement the first-pass Hermes-native BMad workflow plugin using a registry-driven artifact contract architecture, one schema file per tool, and an importable package layout under a hyphenated project root.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [bmad, hermes, plugin, artifact-contracts, workflow-routing, python]
    related_skills: [bmad-operating-model, bmad-artifact-policy, bmad-dev-story, bmad-state-check]
---

# BMad Workflow Plugin Implementation

## When to Use

Use when building or extending the Hermes-native BMad workflow plugin that enforces structured artifacts and deterministic workflow routing.

This is especially relevant when:
- creating the first plugin scaffold
- implementing tool-backed workflow routing for `what comes next`
- enforcing template-driven artifacts like `story` and `sprint_status`
- working in a project root whose directory name contains a hyphen and is not directly importable as a Python package

## Core Approach

Use a layered architecture with these major parts:
- `registry/` for machine-readable artifact contracts
- `schemas/` for shared models plus one schema file per tool
- `paths/` for canonical and legacy artifact path resolution
- `parsers/` for structured parsing of markdown and YAML artifacts
- `validators/` for contract validation and legal transition checks
- `mutations/` for safe contract-aware edits
- `state/` for normalized `_bmad/state.json` handling
- `routing/` for deterministic workflow guidance
- `services/` for high-level orchestration
- `tools/` for thin Hermes tool adapters

## Important Architecture Decision

Do NOT use one giant schema file for all tool I/O.

Preferred long-term layout:
- shared common schema modules
- shared artifact/state domain models
- one schema file per tool

Recommended schema package:
- `schemas/common.py`
- `schemas/artifact_models.py`
- `schemas/bmad_get_state.py`
- `schemas/bmad_get_artifact_contract.py`
- `schemas/bmad_create_artifact_from_template.py`
- `schemas/bmad_validate_artifact.py`
- `schemas/bmad_read_artifact.py`
- `schemas/bmad_update_artifact_section.py`
- `schemas/bmad_sync_story_status.py`
- `schemas/bmad_next_workflow.py`

This is more maintainable than a monolithic schema module and avoids painful rewiring later.

## Critical Implementation Finding

If the project root has a hyphenated directory name such as:
- `/home/reagulus/projects/bmad-workflow-plugin`

then Python imports like `import bmad_workflow_plugin...` should NOT rely on the root directory itself.

Instead, create a real importable package directory inside the project root:

```text
/home/reagulus/projects/bmad-workflow-plugin/
  bmad_workflow_plugin/
    __init__.py
    ...
```

Put the actual Python package modules under that internal package directory.

This avoids brittle import behavior and keeps the project root name decoupled from the import path.

## First-Pass Artifact Contracts

Implement these first:
- `story`
- `sprint_status`

Treat them as contracts, not suggestions.

### `story`
- source template: BMad `create-story/template.md`
- canonical BMad/Hermes path: `_bmad/artifacts/stories/{story_key}.md`
- enforce required sections and legal status transitions
- do not allow `dev-story` to rewrite the story wholesale

### `sprint_status`
- source template: BMad `sprint-status-template.yaml`
- canonical BMad/Hermes path: `_bmad/artifacts/state/sprint-status.yaml`
- enforce legal status values, ordered entries, and valid transitions

## First-Pass Tools

Implement these tools first:
- `bmad_get_state`
- `bmad_init_project`
- `bmad_migrate_state`
- `bmad_get_artifact_contract`
- `bmad_create_artifact_from_template`
- `bmad_validate_artifact`
- `bmad_read_artifact`
- `bmad_update_artifact_section`
- `bmad_sync_story_status`
- `bmad_next_workflow`

## Canonical Build Order

Build in this order:

1. schema and registry foundation
2. path resolver
3. markdown section parser
4. story parser
5. story validator
6. sprint status parser and validator
7. state reader/normalizer/writer
8. routing rules and workflow router
9. services
10. tool handlers
11. plugin entrypoint

## Concrete First Batch

The first working vertical slice should implement:
- `registry/loader.py`
- `paths/resolver.py`
- `parsers/markdown_sections.py`
- `parsers/story_parser.py`
- `validators/story_validator.py`

This gives a real minimum slice around story contract loading, path resolution, parsing, and validation before broader workflow automation.

## Validation and Mutation Rules

- artifact mutation must be transactional: parse -> permission check -> apply in memory -> validate -> write
- story files cannot be rewritten wholesale except during create-story initialization
- sprint status transitions must be checked against contract rules before writing
- workflow routing should live in `routing/` and `services/`, not in the tool handlers
- legacy path support should be isolated in `paths/resolver.py`

## Durable Reference Pattern

When doing major architecture work like this, save design references inside a relevant BMad skill under `references/` so they survive session changes.

For this project, useful durable references include:
- canonical plugin implementation layout
- starter skeleton with module/class/function names
- continuation note in the project root

## Project Environment Setup (uv)

This project has no pyproject.toml by default. When resuming in a fresh session you must
bootstrap the test environment before anything else:

1. Create a valid pyproject.toml — critical pitfall: uv init merges `dependencies` into
   `[tool.setuptools.packages.find]` if the section is misordered. Keep them separate:

```toml
[project]
name = "bmad-workflow-plugin"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["pyyaml>=6.0.3"]

[tool.setuptools.packages.find]
where = ["."]
include = ["bmad_workflow_plugin*"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[dependency-groups]
dev = ["pytest>=9.0.2"]
```

2. Install the package editable into the venv:
   `uv pip install -e .`
   NOT `uv add --editable .` — that goes via the workspace member mechanism and
   does NOT install into site-packages automatically.

3. Run tests with: `uv run pytest tests/ -v`

## Session Cut-Off: Test File SyntaxErrors

When a session is cut off mid-write, test files that use multi-line string literals
for artifact fixture content often end up with the raw markdown embedded without
triple-quote delimiters. Symptoms: `SyntaxError: invalid syntax` at a line that
looks like a comment or YAML key inside a function body.

Fix: wrap the raw text in triple quotes. Example pattern:

```python
def test_foo():
    text = """# Story 1.2: Title
Status: ready-for-dev
...
"""
    doc = Parser().parse('/tmp/slug.md', text)
```

Check all test files that import from `bmad_workflow_plugin` if you see a batch of
SyntaxErrors on collection.

## PathResolver Ambiguity Rule

If both the preferred and any legacy-compatible path exist on disk simultaneously,
`resolve_artifact_path` must return `ambiguous=True` and `path=None`. The caller
must reconcile before proceeding. Do not silently prefer the preferred path when
the legacy path also exists — that hides a data consistency problem.

## TemplateRenderer Escape Sequences

`{{{{` and `}}}}` are the escape sequences for literal `{{` and `}}` in templates
(Jinja2 convention for double-brace literals). The renderer must pre-process these
before running the block-substitution regex, using null-byte sentinels, then restore
them after substitution. Any test asserting `{{{{ name }}}}` → `{{ name }}` exercises
this path.

## Pre-Implementation Audit (do before adding more code)

Before extending the plugin significantly, audit against the real BMad source
(https://github.com/bmad-code-org/BMAD-METHOD) and against Hermes internals.

Key things to verify:
- do the workflow_registry.yaml `recommended_skill` entries point at real skills?
- are there duplicate workflow entries (bmad-* duplicates) for the same concept?
- does the path convention match BMad's `_bmad-output/` and `_bmad/core/config.yaml`?
- are any skills hardcoded to personal paths (`/home/reagulus/projects/`)?
- is there a mechanical tool for each "init" step (not just a doctrine skill)?

Write audit findings to CONTINUE-HERE.md before implementing anything new.

## Hermes MCP Server Integration

The correct integration path for the bmad-workflow-plugin is a FastMCP stdio server,
not entry_points, not direct tool file registration in Hermes source.

### How Hermes loads external tools

Hermes has two extension mechanisms:
1. **Native MCP client** (correct path) — add an entry under `mcp_servers:` in
   `~/.hermes/config.yaml`. Hermes connects at startup via stdio, discovers tools via
   MCP protocol, registers them as `mcp_{server_name}_{tool_name}`. No source changes.
2. **Direct tool file** — tool files in `~/.hermes/hermes-agent/tools/` calling
   `registry.register()` at import time. Requires modifying Hermes source. Not suitable
   for user-space plugins.

### Creating the MCP server

Add `bmad_workflow_plugin/mcp_server.py` using FastMCP:

```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("bmad")   # tools appear as mcp_bmad_*
```

def bmad_get_state(project_root: str) -> str:
    ...

if __name__ == '__main__':
    mcp.run()
```

Each tool function should:
- take only JSON-serializable primitive args (str, Optional[str], bool)
- accept JSON string args for complex inputs (template_vars, operations) and parse them
  inside the function — MCP cannot pass dicts directly
- return a JSON string (serialize with a recursive dataclass-to-dict helper)
- have a docstring — FastMCP uses it as the tool description

### Config.yaml entry

```yaml
mcp_servers:
  bmad:
    command: "uv"
    args:
      - "run"
      - "--project"
      - "/home/reagulus/projects/bmad-workflow-plugin"
      - "python"
      - "-m"
      - "bmad_workflow_plugin.mcp_server"
    timeout: 30
    connect_timeout: 15
```

Hermes must be restarted after adding this entry. Tools then appear as
`mcp_bmad_get_state`, `mcp_bmad_next_workflow`, etc.

### MCP server pitfalls

**Pitfall 1: Schema classes imported by tools must actually exist.**
If `plugin.py` imports tool classes and those tools import schema classes, any missing
class causes an `ImportError` at MCP server startup. Check all schema files match what
the tool layers import before testing. Common symptom: `ImportError: cannot import name
'XResponseData'` — add the missing dataclass to the schema file.

**Pitfall 2: Tool signatures must match the underlying schema exactly.**
The MCP server function params are independent of the schema dataclasses. If the MCP
function passes `query=...` but the underlying tool's `WorkflowHelpRequest` uses
`workflow_id/phase/list_all`, the tool will raise `TypeError: unexpected keyword argument`.
Cross-check every MCP tool function's kwargs against the corresponding schema `__init__`.

**Pitfall 3: `uv add --editable .` does not install into site-packages.**
Use `uv pip install -e .` instead. Without it, `bmad_workflow_plugin` is not importable
by the MCP server subprocess and it will fail with `ModuleNotFoundError`.

**Pitfall 4: `uv add --dev --editable .` workspace member error.**
If pyproject.toml uses `[tool.uv.workspace]`, uv may refuse `uv add --editable .`
with "self-dependencies are not permitted without --dev or --optional". Use
`uv pip install -e .` which bypasses the workspace mechanism entirely.

### Smoke test before wiring into config.yaml

```python
# Verify tools register
from bmad_workflow_plugin.mcp_server import mcp
tools = mcp._tool_manager.list_tools()
print([t.name for t in tools])

# Verify MCP protocol handshake
echo '{"jsonrpc":"2.0","id":1,"method":"initialize",...}' | python -m bmad_workflow_plugin.mcp_server
# Should return a valid JSON-RPC initialize response

# Verify tool logic
from bmad_workflow_plugin.mcp_server import bmad_get_state, bmad_next_workflow
import tempfile, json
d = json.loads(bmad_get_state(tempfile.mkdtemp()))
assert d['data']['state_regime'] == 'missing'
```

## Story Contract vs Template Alignment Rule

When reviewing or extending story contracts, always verify that the story template
includes every section the contract declares — required or optional.

A mismatch between contract and template is a silent behavior trap:
- the contract may declare `review_findings`, `qa_findings`, `evidence_verification`
- if the template omits them, agents creating stories have no section to append to
- agents then create standalone review/QA files instead, causing artifact sprawl
- real exported projects reflect this: code-review files proliferate because the template
  never gave agents a canonical append target inside the story

Fix: move those sections from optional to required in the contract AND add them to the
template. Both must be updated together or the gap just shifts.

Audit trigger: if you see many standalone `code-review-*.md` or `qa-report-*.md` files
in real project exports, check whether the story template is missing those sections.
Do not try to detect these stray files in migration heuristics — fix the source template
instead so future stories are scaffolded correctly.

## Service-Level Lazification Checklist

Before lazifying internals of a service, ask:
1. Does every code path through the service use all its constructed components?
   If yes, lazy construction buys nothing — the components will always be instantiated.
2. Are the sub-components truly expensive to construct (I/O, registry loads, heavy parsers)?
   Zero-arg stateless helper classes (StateReader, StateNormalizer, SprintStatusParser, etc.)
   cost effectively nothing to construct. Do not lazify them.
3. Does the plugin container already provide outer lazy loading?
   If the service itself is a lazy property on the plugin, inner lazy construction is
   redundant — the service is only created when a tool that needs it is invoked.

Apply lazy-loading at the level where it actually reduces work per request:
- plugin container (service properties) — yes, always lazy
- ArtifactService parser/validator/mutator dispatch — yes, many artifact types, only one used per call
- WorkflowRouter state/path/parser sub-components — yes, missing-state fast-path skips them
- Individual service sub-components that are always used — no, leave eager

## ArtifactService Lazy-Loading Pattern

When `ArtifactService` grows across many artifact types, do not instantiate every parser,
validator, and mutator in `__init__`.

Prefer this pattern:
- keep per-kind factory maps (`parser_factories`, `validator_factories`, `mutator_factories`)
- resolve components on first use per `artifact_type`
- cache the instantiated component in `_parsers`, `_validators`, `_mutators`
- allow factory-map injection in tests so lazy behavior can be verified without monkeypatching imports
- if possible, use import-on-demand factories so simple operations do not pay all module import costs up front

Minimum verification:
- `ArtifactService()` construction should not instantiate any parser/validator/mutator
- `read_artifact()` should instantiate only the parser/validator for the requested type
- repeated reads should reuse cached instances
- `update_artifact_sections()` should instantiate the mutator only when mutation is actually invoked
- apply the same idea to `WorkflowRouter`: create state/path/parser components only when the current routing path actually needs them
- extend the same rule upward: `WorkflowService` should lazy-create its router, and thin wrappers like workflow-help should reuse that service instead of constructing their own router path
- in the plugin container, prefer lazy service properties plus `get_tool(name)` caching; in MCP entrypoints, resolve the one needed tool directly instead of rebuilding the whole tool map on every request

## Phase 1–3 E2E Coverage Notes

When adding broader artifact-service coverage for Phase 1–3:
- exercise the full `ArtifactService` flow: create -> read -> validate -> update -> read again
- cover all registered Phase 1–3 artifact types, not just one example per phase
- use contract-backed destination paths in assertions so path resolution stays under test
- treat end-to-end failures as likely parser/contract/template integration bugs, not as test noise
- prefer fixing parser canonicalization at the source when human-readable template headings differ from canonical contract section IDs
- PRFAQ needs special handling because the real template shape does not map 1:1 to naive markdown section parsing; synthesize canonical sections like `headline` and `press_release` from the actual document structure

## MCP Integration Coverage Notes

When adding MCP-server-level coverage:
- test the FastMCP tool registry directly via `mcp._tool_manager.list_tools()`
- test the real stdio handshake using the same launch shape Hermes uses: `uv run --project <root> python -m bmad_workflow_plugin.mcp_server`
- do not rely on bare `python -m ...` from an arbitrary cwd; that can fail even when the configured MCP server launch works
- add at least one direct round-trip through MCP-exposed functions for a real workflow path (for example `bmad_init_project` then `bmad_get_state`)
- include one registry/alias-sensitive MCP-exposed call like `bmad_workflow_help` so routing fixes are exercised through the server surface

## Live MCP Verification on a Real Project

After changing MCP-exposed tools or compatibility behavior, do not stop at unit/integration tests.
Smoke the *live* `mcp_bmad_*` surface against a real project root from Hermes itself.

Recommended sequence:
1. Re-run the plugin test suite.
2. Use the live MCP tools already loaded in Hermes on a real project root.
3. For migration-related changes, run this exact shape:
   - `mcp_bmad_get_state(project_root)`
   - `mcp_bmad_migrate_state(project_root)`
   - `mcp_bmad_get_state(project_root)` again
   - `mcp_bmad_next_workflow(project_root)`
4. Confirm the post-migration handoff stays conservative and truthful (typically `bmad-state-check` for partially-normalized state).
5. Record concrete evidence such as backup path, legacy history count, and the resulting `state_regime`.

Why this matters:
- the currently running Hermes session may or may not still be using a stale MCP subprocess
- continuation notes can become stale in either direction: they may warn that the live server is old even when the current session already has the new tools
- real projects surface behavior that synthetic fixtures do not, especially around `_bmad/config.yaml`, legacy `_bmad/state.json`, and migration side effects

## Documentation Reconciliation Rule

After live verification, reconcile `CONTINUE-HERE.md` and `README.md` with code reality.
In this project, stale docs were a real source of confusion.

Specifically check for:
- old test-count baselines
- outdated package/plugin naming
- stale claims that a loader is uncached when the code now caches it
- stale claims that Hermes must be restarted before a tool exists, when the current session already proves the tool is live
- README text that still describes a scaffold after the plugin has become operational

## bmad_init_project Tool Notes

When implementing `bmad_init_project`:
- make it mechanical: create directories/files directly rather than delegating scaffold creation to doctrine skills
- write `_bmad/state.json`, `_bmad/notes.md`, and optionally `_bmad/core/config.yaml`
- preserve meaningful existing files by default; report preserved vs created paths explicitly
- create the configured legacy-compatible output root so BMad path compatibility works from the start
- wire the tool through schema -> tool -> plugin -> MCP server, then add focused tests for creation and preservation behavior

## Routing Hole Fix Notes

When fixing workflow routing holes:
- inspect both `workflow_registry.yaml` and `routing/workflow_router.py` — the router may hardcode workflow IDs or skills that bypass the registry
- keep `bmad-*` as canonical workflow IDs and add unprefixed aliases for backwards compatibility
- do not point executable workflows like sprint planning, create story, or retrospective at `bmad-operating-model`; that is doctrine, not execution
- if a workflow has no real skill target, create a dedicated wrapper skill rather than routing to doctrine
- add tests for alias resolution and for concrete routing outcomes from realistic sprint-status fixtures
- prefer canonical routing outputs like `bmad-sprint-planning`, `bmad-create-story`, and `bmad-retrospective`

## Gap 3 Compatibility Implementation Notes

When implementing BMad-native path/config compatibility:
- support both `_bmad/core/config.yaml` and the real exported `_bmad/config.yaml` layout; prefer core/config when both exist
- if `_bmad/state.json` is missing but supported BMad config exists, treat the project as `legacy_only` rather than `missing`
- surface upstream config fields inside normalized state under a dedicated key like `normalized_state['bmad_config']`
- legacy path resolution must rewrite `_bmad-output/` roots to the configured `output_folder`
- enrich missing identity with `project_name` from config when building preferred paths
- for story resolution, derive compatibility aliases from `story_key` such as `story-{story_key}` and short numeric forms like `1-1`
- for legacy/project-scoped artifacts, allow a wildcard fallback when placeholders remain unresolved so a unique on-disk match can still be found
- use tighter glob patterns for version placeholders (for example numeric-only version wildcards) so `prd-v2.md` does not collide with `prd-validation-report-v2.md`
- `create_from_template()` should pass the full template vars as identity, not only `story_key`
- add focused tests covering config-only projects, custom output folders, unique glob-based resolution, and real exported filename patterns

## Real Export Verification Findings

Real exported projects may not match the initial idealized fixture layout.
Observed compatibility cases worth encoding:
- planning artifacts often live directly under `_bmad-output/planning-artifacts/` rather than nested artifact-type directories
- common exported filenames include `product-brief-<Project>.md`, dated brief variants, `prd.md`, `prd-<Project>.md`, `prd-vN.md`, `prd-validation-report*.md`, `ux-design-specification.md`, `architecture.md`, and `epics-and-stories*.md`
- implementation stories often live under `_bmad-output/implementation-artifacts/stories/`
- sprint status appears in multiple real formats: nested YAML story lists, markdown status tables, YAML with markdown appendices, and sprint-level `story_ids` plus sprint status
- some real exports are intentionally ambiguous (for example both `prd.md` and `prd-v2.md`); preserve explicit ambiguity instead of guessing

## Completion Standard

A good first-pass plugin implementation locks in:
- importable package structure
- registry-driven contracts
- schema organization
- deterministic path resolution
- working story parsing and validation
- a FastMCP stdio server wired into ~/.hermes/config.yaml
- a pre-implementation audit against BMad source and Hermes internals
- a scaffold that can expand without rewiring the architecture later
