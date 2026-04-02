"""
BMad Workflow Plugin — FastMCP stdio server.

Exposes all bmad_workflow_plugin tools as MCP tools so Hermes can discover
and call them via the native MCP client.
"""

from __future__ import annotations

import dataclasses
import json
import logging
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from bmad_workflow_plugin.plugin import BmadWorkflowPlugin

logger = logging.getLogger(__name__)

mcp = FastMCP("bmad")

_plugin: BmadWorkflowPlugin | None = None


def _get_plugin() -> BmadWorkflowPlugin:
    global _plugin
    if _plugin is None:
        _plugin = BmadWorkflowPlugin()
    return _plugin


def _to_json(obj: Any) -> str:
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return json.dumps(_dc_to_dict(obj), indent=2)
    return json.dumps(obj, indent=2, default=str)


def _dc_to_dict(obj: Any) -> Any:
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: _dc_to_dict(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
    if isinstance(obj, list):
        return [_dc_to_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _dc_to_dict(v) for k, v in obj.items()}
    if hasattr(obj, 'value') and type(obj).__bases__ and any(
        b.__name__ in ('Enum', 'str') for b in type(obj).__mro__
    ):
        return obj.value
    return obj


def _execute_tool(name: str, payload: dict[str, Any]):
    tool = _get_plugin().get_tool(name)
    return tool.execute(payload)


@mcp.tool()
def bmad_get_state(project_root: str) -> str:
    """
    Read and return the normalized BMad workflow state for a project.

    Returns state_regime (missing/legacy_only/partially_normalized/normalized),
    the raw state from _bmad/state.json (if present), and any legacy indicators.
    Use this to understand current project workflow position before calling
    bmad_next_workflow.
    """
    return _to_json(_execute_tool('bmad_get_state', {'project_root': project_root}))


@mcp.tool()
def bmad_init_project(
    project_root: str,
    project_name: Optional[str] = None,
    create_core_config: bool = True,
    output_folder: Optional[str] = None,
    user_name: Optional[str] = None,
    communication_language: Optional[str] = None,
    document_output_language: Optional[str] = None,
    user_skill_level: Optional[str] = None,
) -> str:
    """
    Mechanically initialize a project-local BMad scaffold under `_bmad/`.

    Creates canonical state/artifact directories, writes `_bmad/state.json`,
    writes `_bmad/notes.md`, and optionally writes `_bmad/core/config.yaml`
    for upstream BMad compatibility. Existing meaningful files are preserved.
    """
    return _to_json(_execute_tool('bmad_init_project', {
        'project_root': project_root,
        'project_name': project_name,
        'create_core_config': create_core_config,
        'output_folder': output_folder,
        'user_name': user_name,
        'communication_language': communication_language,
        'document_output_language': document_output_language,
        'user_skill_level': user_skill_level,
    }))


@mcp.tool()
def bmad_migrate_state(project_root: str) -> str:
    """
    Non-destructively migrate a legacy `_bmad/state.json` (or config-only export)
    into BMad-compatible normalized live state.
    """
    return _to_json(_execute_tool('bmad_migrate_state', {'project_root': project_root}))


@mcp.tool()
def bmad_next_workflow(project_root: str, target_story_key: Optional[str] = None) -> str:
    """
    Compute the next recommended workflow for a project based on current state.
    """
    return _to_json(_execute_tool('bmad_next_workflow', {
        'project_root': project_root,
        'target_story_key': target_story_key,
    }))


@mcp.tool()
def bmad_get_artifact_contract(artifact_type: str) -> str:
    """
    Return the registered artifact contract for a given artifact type.
    """
    return _to_json(_execute_tool('bmad_get_artifact_contract', {'artifact_type': artifact_type}))


@mcp.tool()
def bmad_create_artifact_from_template(
    project_root: str,
    artifact_type: str,
    template_vars: str,
    destination_path: Optional[str] = None,
    overwrite: bool = False,
) -> str:
    """
    Create an artifact file from the registered template for an artifact type.
    """
    try:
        vars_dict = json.loads(template_vars)
    except json.JSONDecodeError as e:
        return json.dumps({
            'success': False,
            'errors': [{'code': 'invalid_template_vars', 'message': str(e)}],
        })

    return _to_json(_execute_tool('bmad_create_artifact_from_template', {
        'project_root': project_root,
        'artifact_type': artifact_type,
        'template_vars': vars_dict,
        'destination_path': destination_path,
        'overwrite': overwrite,
    }))


@mcp.tool()
def bmad_validate_artifact(
    project_root: str,
    artifact_type: str,
    artifact_path: Optional[str] = None,
) -> str:
    """
    Validate an artifact file against its registered contract.
    """
    return _to_json(_execute_tool('bmad_validate_artifact', {
        'project_root': project_root,
        'artifact_type': artifact_type,
        'artifact_path': artifact_path,
    }))


@mcp.tool()
def bmad_read_artifact(
    project_root: str,
    artifact_type: str,
    artifact_path: Optional[str] = None,
) -> str:
    """
    Read and parse an artifact file, returning its structured fields.
    """
    return _to_json(_execute_tool('bmad_read_artifact', {
        'project_root': project_root,
        'artifact_type': artifact_type,
        'artifact_path': artifact_path,
    }))


@mcp.tool()
def bmad_update_artifact_section(
    project_root: str,
    artifact_type: str,
    artifact_path: str,
    workflow_id: str,
    operations: str,
) -> str:
    """
    Apply structured mutations to an artifact file.
    """
    try:
        parsed_operations = json.loads(operations)
    except json.JSONDecodeError as e:
        return json.dumps({
            'success': False,
            'errors': [{'code': 'invalid_operations', 'message': str(e)}],
        })

    return _to_json(_execute_tool('bmad_update_artifact_section', {
        'project_root': project_root,
        'artifact_type': artifact_type,
        'artifact_path': artifact_path,
        'workflow_id': workflow_id,
        'operations': parsed_operations,
    }))


@mcp.tool()
def bmad_sync_story_status(
    project_root: str,
    story_key: str,
    new_status: str,
    source_workflow: str,
    reason: Optional[str] = None,
) -> str:
    """
    Atomically update a story's status in both the story artifact and sprint-status.yaml.
    """
    return _to_json(_execute_tool('bmad_sync_story_status', {
        'project_root': project_root,
        'story_key': story_key,
        'new_status': new_status,
        'source_workflow': source_workflow,
        'reason': reason,
    }))


@mcp.tool()
def bmad_workflow_help(
    workflow_id: Optional[str] = None,
    phase: Optional[str] = None,
    list_all: bool = False,
) -> str:
    """
    Return help text and workflow listings for BMad workflows.
    """
    return _to_json(_execute_tool('bmad_workflow_help', {
        'workflow_id': workflow_id,
        'phase': phase,
        'list_all': list_all,
    }))


if __name__ == '__main__':
    mcp.run()
