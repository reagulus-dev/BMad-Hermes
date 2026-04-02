from __future__ import annotations

import json
from pathlib import Path

import yaml

from bmad_workflow_plugin.plugin import BmadWorkflowPlugin
from bmad_workflow_plugin.services.init_service import InitService


def test_init_service_creates_canonical_scaffold(tmp_path: Path) -> None:
    result = InitService().init_project(
        project_root=str(tmp_path),
        project_name='demo-app',
        output_folder='legacy-output',
        user_name='reagulus',
    )

    state_path = tmp_path / '_bmad' / 'state.json'
    config_path = tmp_path / '_bmad' / 'core' / 'config.yaml'
    notes_path = tmp_path / '_bmad' / 'notes.md'

    assert state_path.exists()
    assert config_path.exists()
    assert notes_path.exists()
    assert (tmp_path / '_bmad' / 'artifacts' / 'stories').exists()
    assert (tmp_path / 'legacy-output').exists()

    state = json.loads(state_path.read_text(encoding='utf-8'))
    config = yaml.safe_load(config_path.read_text(encoding='utf-8'))

    assert state['project_name'] == 'demo-app'
    assert state['workflow_status'] == 'idle'
    assert config['project_name'] == 'demo-app'
    assert config['output_folder'] == 'legacy-output'
    assert result['state_path'] == str(state_path)


def test_init_service_preserves_existing_meaningful_files(tmp_path: Path) -> None:
    bmad = tmp_path / '_bmad'
    (bmad / 'core').mkdir(parents=True)
    (bmad / 'state.json').write_text('{"schema_version":"2.0","project_name":"keep-me"}\n', encoding='utf-8')
    (bmad / 'core' / 'config.yaml').write_text('project_name: keep-me\noutput_folder: keep-output\n', encoding='utf-8')

    result = InitService().init_project(project_root=str(tmp_path), project_name='new-name', output_folder='new-output')

    state = json.loads((bmad / 'state.json').read_text(encoding='utf-8'))
    config = yaml.safe_load((bmad / 'core' / 'config.yaml').read_text(encoding='utf-8'))

    assert state['project_name'] == 'keep-me'
    assert config['project_name'] == 'keep-me'
    assert any(path.endswith('_bmad/state.json') for path in result['preserved_paths'])
    assert any(path.endswith('_bmad/core/config.yaml') for path in result['preserved_paths'])


def test_bmad_init_project_tool_is_registered_and_returns_success(tmp_path: Path) -> None:
    tools = BmadWorkflowPlugin().build_tools()
    response = tools['bmad_init_project'].execute({
        'project_root': str(tmp_path),
        'project_name': 'tool-demo',
        'create_core_config': True,
        'output_folder': 'compat-output',
    })

    assert response.success is True
    assert response.data is not None
    assert response.data.project_name == 'tool-demo'
    assert response.data.config_path is not None
    assert response.data.legacy_output_root.endswith('/compat-output')
