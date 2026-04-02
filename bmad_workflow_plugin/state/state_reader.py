from __future__ import annotations

from pathlib import Path
import json

from bmad_workflow_plugin.state.bmad_config import BmadConfigReader


class StateReader:
    def read(self, project_root: str) -> dict | None:
        path = Path(project_root) / '_bmad' / 'state.json'
        if not path.exists():
            config = BmadConfigReader().read(project_root)
            if config is None:
                return None
            return {
                'projectName': config.get('project_name') or Path(project_root).name,
                'projectPath': str(Path(project_root).resolve()),
                'currentPhase': None,
                'activeWorkflow': None,
                'completedWorkflows': [],
                '__bmad_config__': config,
            }
        with path.open('r', encoding='utf-8') as f:
            payload = json.load(f)

        config = BmadConfigReader().read(project_root)
        if config is not None and isinstance(payload, dict):
            payload.setdefault('__bmad_config__', config)
        return payload
