# BMad-Hermes

A Hermes-native plugin that brings the [BMad Method](https://github.com/bmad-code-org/BMAD-METHOD) into the Hermes AI agent environment as a first-class, contract-backed workflow system.

---

## What it is

BMad is a multi-agent, multi-phase software delivery method. Projects move through four phases — Analysis, Planning, Solutioning, and Implementation — each producing structured artifacts that feed the next phase.

This plugin wires that method into Hermes by providing:

- **Project state management** — initialize and normalize `_bmad/state.json` per project, including non-destructive migration of legacy BMad exports
- **Artifact contracts** — schema-enforced creation, reading, validation, and mutation of all Phase 1–4 artifacts (PRD, architecture, stories, sprint status, etc.)
- **Workflow routing** — deterministic "what comes next" decisions based on current project state, sprint status, and story progress
- **MCP server** — a FastMCP stdio server so Hermes exposes all tools as `mcp_bmad_*` without any Hermes source changes
- **Bundled skills** — all `bmad-*` Hermes skills included so the agent has the policy doctrine to go with the mechanical tools

---

## Tool surface

| Tool | Purpose |
|------|---------|
| `bmad_get_state` | Read and normalize current project state |
| `bmad_init_project` | Scaffold `_bmad/` directory structure for a new project |
| `bmad_migrate_state` | Non-destructively migrate legacy BMad export into normalized live state |
| `bmad_next_workflow` | Route to the next recommended workflow/skill based on project state |
| `bmad_workflow_help` | Look up workflow guidance by name or phase |
| `bmad_get_artifact_contract` | Inspect the contract for any artifact type |
| `bmad_create_artifact_from_template` | Create a new artifact file from its canonical template |
| `bmad_read_artifact` | Parse and read an artifact with contract validation |
| `bmad_validate_artifact` | Validate an existing artifact against its contract |
| `bmad_update_artifact_section` | Mutate a specific section of an artifact |
| `bmad_sync_story_status` | Atomically update story status in sprint-status.yaml and state.json |

---

## Design principles

- **Route narrowly** — the plugin identifies the next workflow/skill explicitly; the agent does not guess
- **Load on demand** — services, parsers, validators, and mutators are instantiated only when actually needed
- **Contracts over convention** — artifact shape is enforced mechanically; skills provide judgment
- **Story as anchor** — review findings, QA results, and evidence all append to the story artifact; standalone files only for cross-story or release-wide work

---

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Hermes AI agent environment

---

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/reagulus-dev/BMad-Hermes.git
cd BMad-Hermes
```

### 2. Create a virtualenv and install the package

```bash
uv venv
uv pip install -e .
```

To also install dev dependencies (pytest):

```bash
uv sync --group dev
```

> **Note:** Use `uv pip install -e .` — do not use `uv add --editable .` for this project; it may not install the package into site-packages the way the MCP subprocess expects.

### 3. Verify the install

```bash
.venv/bin/pytest tests/ -v
```

Expected: `100/100` tests passing.

### 4. Smoke-test the MCP server

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0"}}}' \
  | .venv/bin/python -m bmad_workflow_plugin.mcp_server
```

Expected: a JSON-RPC initialize response with `serverInfo.name` = `bmad`.

### 5. Install the bundled skills into Hermes

```bash
cp -r skills/bmad-* ~/.hermes/skills/software-development/
```

### 6. Register the MCP server in Hermes

Add this to `~/.hermes/config.yaml` (adjust the path to wherever you cloned the repo):

```yaml
mcp_servers:
  bmad:
    command: "uv"
    args:
      - "run"
      - "--project"
      - "/absolute/path/to/BMad-Hermes"
      - "python"
      - "-m"
      - "bmad_workflow_plugin.mcp_server"
    timeout: 30
    connect_timeout: 15
```

### 7. Restart Hermes

After restart, the tools appear as `mcp_bmad_bmad_get_state`, `mcp_bmad_bmad_next_workflow`, etc.

---

## Verifying the live tool surface

Once Hermes is running with the MCP server loaded, run this sequence on any project:

```
mcp_bmad_bmad_get_state        # inspect current state regime
mcp_bmad_bmad_next_workflow    # get the recommended next workflow
mcp_bmad_bmad_workflow_help    # look up any workflow by name
```

For a legacy BMad project:

```
mcp_bmad_bmad_get_state        # confirms legacy_only or partially_normalized
mcp_bmad_bmad_migrate_state    # non-destructive migration, creates timestamped backup
mcp_bmad_bmad_get_state        # confirms partially_normalized, next = bmad-state-check
mcp_bmad_bmad_next_workflow    # routes to bmad-state-check conservatively
```

---

## Project layout

```
bmad_workflow_plugin/
  registry/         artifact contracts + workflow registry (YAML)
  paths/            canonical + legacy-compatible path resolution
  parsers/          markdown/YAML artifact parsing
  validators/       contract validation
  mutations/        section-level artifact updates + template rendering
  state/            state read / normalize / write + BMad config compatibility
  routing/          next-workflow decision logic
  services/         orchestration layer
  tools/            MCP tool adapters
  templates/        canonical artifact templates (story, PRD, architecture, etc.)
  mcp_server.py     FastMCP stdio server entrypoint

skills/             bundled bmad-* Hermes skills (copy to ~/.hermes/skills/software-development/)
tests/              full test suite (100 tests)
```

---

## Artifact coverage

### Phase 1 — Analysis
- `brainstorming_session`
- `product_brief`
- `prfaq`

### Phase 2 — Planning
- `prd`
- `prd_validation_report`
- `ux_design`

### Phase 3 — Solutioning
- `architecture`
- `epics_and_stories`
- `project_context`

### Phase 4 — Implementation
- `story` (includes `## Review Findings`, `## QA Findings`, `## Evidence / Verification` sections)
- `sprint_status`
- `review_record` (cross-story reviews)
- `qa_record` (cross-story QA sweeps)

---

## BMad config compatibility

The plugin recognizes both layout styles produced by real BMad exports:

- `_bmad/core/config.yaml` (canonical Alice layout)
- `_bmad/config.yaml` (real exported BMad layout)

Config fields (`project_name`, `output_folder`, `user_name`, `communication_language`, `document_output_language`, `user_skill_level`) are surfaced under `normalized_state.bmad_config` after a `bmad_get_state` call.

Path resolution honors configurable `output_folder` so artifacts under custom roots (not just `_bmad-output/`) are found correctly.

---

## State regimes

`bmad_get_state` returns one of:

| Regime | Meaning |
|--------|---------|
| `missing` | No `_bmad/` state or config found |
| `legacy_only` | Legacy BMad camelCase state or config-only export |
| `partially_normalized` | Mix of legacy and normalized fields (post-migration) |
| `normalized_ready` | Fully normalized Alice live state |
| `normalized_stale` | Normalized but `updated_at` is more than 30 days old |

`bmad_next_workflow` uses the regime as the primary routing gate before inspecting sprint/story status.

---

## Running tests

```bash
cd BMad-Hermes
.venv/bin/pytest tests/ -v
```

Expected baseline: `100/100` passing.

---

## Common pitfalls

- **Stale Hermes session** — after source changes, restart Hermes to pick up the updated MCP subprocess
- **Wrong launch shape** — always use `uv run --project <path> python -m bmad_workflow_plugin.mcp_server`; a different launch shape can cause import failures even when the package looks correct locally
- **Missing schema or tool kwargs** — MCP startup failures often come from mismatched tool signatures, not import errors; run the smoke test above to catch these before wiring into Hermes
- **Ambiguous artifacts** — projects with multiple PRD versions (e.g. `prd.md` + `prd-v2.md`) are intentionally flagged as ambiguous rather than silently resolved; resolve manually and re-run

---

## See also

- `CONTINUE-HERE.md` — session continuation state and verified next steps
- [BMad Method](https://github.com/bmad-code-org/BMAD-METHOD) — upstream workflow method this plugin implements
