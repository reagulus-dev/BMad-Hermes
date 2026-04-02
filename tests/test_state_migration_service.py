from __future__ import annotations

import json
from pathlib import Path

from bmad_workflow_plugin.plugin import BmadWorkflowPlugin
from bmad_workflow_plugin.services.state_migration_service import StateMigrationService


LEGACY_STATE = {
    'projectName': 'legacy-demo',
    'projectPath': '/tmp/legacy-demo',
    'createdAt': '2026-03-01T00:00:00Z',
    'currentPhase': 'implementation',
    'activeWorkflow': None,
    'completedWorkflows': [
        {'workflowId': 'dev-story', 'outputPath': '_bmad-output/implementation-artifacts/stories/story-1-1-demo.md'},
    ],
}

SPRINT_STATUS_REAL_EXPORT = """metadata:
  project: Legacy Demo
  generated: 2026-03-20 21:10:00+00:00
sprints:
- sprint: 1
  stories:
  - id: 1.1
    title: Completed Story
    status: dev_complete
  - id: 1.2
    title: Next Story
    status: spec_created
"""


def test_state_migration_service_preserves_legacy_history_and_creates_backup(tmp_path: Path) -> None:
    bmad = tmp_path / '_bmad'
    bmad.mkdir(parents=True)
    state_path = bmad / 'state.json'
    state_path.write_text(json.dumps(LEGACY_STATE, indent=2) + '\n', encoding='utf-8')
    (tmp_path / '_bmad' / 'core').mkdir(parents=True, exist_ok=True)
    (tmp_path / '_bmad' / 'core' / 'config.yaml').write_text('project_name: legacy-demo\noutput_folder: _bmad-output\n', encoding='utf-8')

    sprint_path = tmp_path / '_bmad-output' / 'implementation-artifacts' / 'sprint-status.yaml'
    sprint_path.parent.mkdir(parents=True, exist_ok=True)
    sprint_path.write_text(SPRINT_STATUS_REAL_EXPORT, encoding='utf-8')

    result = StateMigrationService(BmadWorkflowPlugin().registry).migrate(str(tmp_path))

    assert result['backup_path'] is not None
    assert Path(result['backup_path']).exists()
    assert result['legacy_history_preserved'] is True
    assert result['legacy_history_count'] == 1
    assert result['recommended_next_workflow'] == 'bmad-state-check'

    migrated = json.loads(state_path.read_text(encoding='utf-8'))
    assert migrated['projectName'] == 'legacy-demo'
    assert migrated['schema_version'] == '2.0'
    assert migrated['legacy_bmad']['preserved'] is True
    assert migrated['legacy_bmad']['completed_workflows'] == LEGACY_STATE['completedWorkflows']
    assert migrated['current_story'] == '1-2'
    assert migrated['last_artifacts'] == [str(sprint_path.resolve())]


def test_bmad_migrate_state_tool_handles_config_only_real_export_layout(tmp_path: Path) -> None:
    (tmp_path / '_bmad').mkdir(parents=True)
    (tmp_path / '_bmad' / 'config.yaml').write_text('project_name: exported-demo\noutput_folder: _bmad-output\n', encoding='utf-8')

    prd_path = tmp_path / '_bmad-output' / 'planning-artifacts' / 'prd-v2.md'
    prd_path.parent.mkdir(parents=True, exist_ok=True)
    prd_path.write_text('# PRD\n', encoding='utf-8')

    sprint_path = tmp_path / '_bmad-output' / 'implementation-artifacts' / 'sprint-status.yaml'
    sprint_path.parent.mkdir(parents=True, exist_ok=True)
    sprint_path.write_text(SPRINT_STATUS_REAL_EXPORT, encoding='utf-8')

    response = BmadWorkflowPlugin().build_tools()['bmad_migrate_state'].execute({'project_root': str(tmp_path)})

    assert response.success is True
    assert response.data is not None
    assert response.data.backup_path is None
    assert response.data.recommended_next_workflow == 'bmad-state-check'
    assert str(prd_path.resolve()) in response.data.last_artifacts
    assert str(sprint_path.resolve()) in response.data.last_artifacts

    state = json.loads((tmp_path / '_bmad' / 'state.json').read_text(encoding='utf-8'))
    assert state['project_name'] == 'exported-demo'
    assert state['current_phase'] == 'implementation'
    assert state['current_story'] == '1-2'
    assert state['workflow_status'] == 'idle'