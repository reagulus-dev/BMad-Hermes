from __future__ import annotations

import json
import subprocess
from pathlib import Path

from bmad_workflow_plugin.mcp_server import (
    bmad_get_state,
    bmad_init_project,
    bmad_migrate_state,
    bmad_workflow_help,
    mcp,
)


def test_mcp_server_registers_expected_tools() -> None:
    tools = mcp._tool_manager.list_tools()
    names = {tool.name for tool in tools}

    assert 'bmad_get_state' in names
    assert 'bmad_init_project' in names
    assert 'bmad_migrate_state' in names
    assert 'bmad_next_workflow' in names
    assert 'bmad_workflow_help' in names
    assert len(names) >= 11


def test_mcp_stdio_initialize_handshake(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parent.parent
    command = [
        'uv',
        'run',
        '--project',
        str(project_root),
        'python',
        '-m',
        'bmad_workflow_plugin.mcp_server',
    ]
    request = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'initialize',
        'params': {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {'name': 'pytest', 'version': '0'},
        },
    }

    proc = subprocess.run(
        command,
        input=json.dumps(request) + '\n',
        text=True,
        capture_output=True,
        cwd=str(tmp_path),
        timeout=20,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout.strip())
    assert payload['result']['serverInfo']['name'] == 'bmad'
    assert 'tools' in payload['result']['capabilities']


def test_mcp_exposed_init_and_get_state_round_trip(tmp_path: Path) -> None:
    init_payload = json.loads(
        bmad_init_project(
            project_root=str(tmp_path),
            project_name='mcp-demo',
            create_core_config=True,
            output_folder='legacy-output',
            user_name='reagulus',
        )
    )

    assert init_payload['success'] is True
    assert init_payload['data']['project_name'] == 'mcp-demo'
    assert init_payload['data']['legacy_output_root'].endswith('/legacy-output')

    state_payload = json.loads(bmad_get_state(str(tmp_path)))
    assert state_payload['success'] is True
    assert state_payload['data']['normalized_state']['bmad_config']['project_name'] == 'mcp-demo'


def test_mcp_workflow_help_accepts_alias_after_registry_alias_fix() -> None:
    payload = json.loads(bmad_workflow_help(workflow_id='project-init'))

    assert payload['success'] is True
    assert payload['data']['workflow_id'] == 'bmad-project-init'
    assert payload['data']['recommended_skill'] == 'bmad-project-init'


def test_mcp_migrate_state_exposed_round_trip_for_config_only_project(tmp_path: Path) -> None:
    bmad = tmp_path / '_bmad'
    bmad.mkdir(parents=True)
    (bmad / 'config.yaml').write_text('project_name: migrate-demo\noutput_folder: _bmad-output\n', encoding='utf-8')

    sprint_path = tmp_path / '_bmad-output' / 'implementation-artifacts' / 'sprint-status.yaml'
    sprint_path.parent.mkdir(parents=True, exist_ok=True)
    sprint_path.write_text(
        'generated: now\nproject: demo\nproject_key: DEMO\ntracking_system: file-system\nstory_location: _bmad/artifacts/stories\ndevelopment_status:\n  1-1-story: backlog\n',
        encoding='utf-8',
    )

    payload = json.loads(bmad_migrate_state(str(tmp_path)))

    assert payload['success'] is True
    assert payload['data']['backup_path'] is None
    assert payload['data']['recommended_next_workflow'] == 'bmad-state-check'
