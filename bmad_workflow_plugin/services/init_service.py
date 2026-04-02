from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import yaml


class InitService:
    """Mechanical project scaffold creation for _bmad and compatibility config."""

    def init_project(
        self,
        project_root: str,
        project_name: str | None = None,
        create_core_config: bool = True,
        output_folder: str | None = None,
        user_name: str | None = None,
        communication_language: str | None = None,
        document_output_language: str | None = None,
        user_skill_level: str | None = None,
    ) -> dict:
        root = Path(project_root).resolve()
        root.mkdir(parents=True, exist_ok=True)

        created_paths: list[str] = []
        preserved_paths: list[str] = []
        notes: list[str] = []

        now = datetime.now(timezone.utc).isoformat()
        canonical_project_name = project_name or root.name
        legacy_output_root = (output_folder or '_bmad-output').strip() or '_bmad-output'

        directories = [
            root / '_bmad',
            root / '_bmad' / 'artifacts',
            root / '_bmad' / 'artifacts' / 'stories',
            root / '_bmad' / 'artifacts' / 'reviews',
            root / '_bmad' / 'artifacts' / 'qa',
            root / '_bmad' / 'artifacts' / 'evidence',
            root / '_bmad' / 'artifacts' / 'corrections',
            root / '_bmad' / 'artifacts' / 'release',
            root / '_bmad' / 'artifacts' / 'handoffs',
            root / '_bmad' / 'artifacts' / 'state',
            root / '_bmad' / 'artifacts' / 'archive',
            root / '_bmad' / 'templates',
            root / '_bmad' / 'core',
            root / legacy_output_root,
        ]

        for path in directories:
            if path.exists():
                preserved_paths.append(str(path))
            else:
                path.mkdir(parents=True, exist_ok=True)
                created_paths.append(str(path))

        state_path = root / '_bmad' / 'state.json'
        if state_path.exists():
            preserved_paths.append(str(state_path))
            notes.append('Preserved existing _bmad/state.json.')
        else:
            state_payload = {
                'schema_version': '2.0',
                'persona': 'Alice',
                'method': 'bmad-hermes',
                'project_name': canonical_project_name,
                'project_root': str(root),
                'created_at': now,
                'updated_at': now,
                'current_phase': 'implementation',
                'workflow_status': 'idle',
                'active_workflow': None,
                'current_epic': None,
                'current_story': None,
                'current_sprint': None,
                'blockers': [],
                'last_artifacts': [],
                'last_review_summary': None,
                'last_evidence_path': None,
                'next_recommended_workflows': [],
                'state_check': {
                    'last_checked_at': None,
                    'trust_level': 'partial',
                    'notes': [],
                },
                'legacy_bmad': {
                    'preserved': (root / legacy_output_root).exists(),
                    'completed_workflows': [],
                },
            }
            state_path.write_text(json.dumps(state_payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
            created_paths.append(str(state_path))

        notes_path = root / '_bmad' / 'notes.md'
        if notes_path.exists():
            preserved_paths.append(str(notes_path))
        else:
            notes_path.write_text(
                '# BMad Project Notes\n\nProject-local notes for workflow context that should stay with the repository.\n',
                encoding='utf-8',
            )
            created_paths.append(str(notes_path))

        config_path = root / '_bmad' / 'core' / 'config.yaml'
        if create_core_config:
            if config_path.exists():
                preserved_paths.append(str(config_path))
                notes.append('Preserved existing _bmad/core/config.yaml.')
            else:
                config_payload = {
                    'project_name': canonical_project_name,
                    'output_folder': legacy_output_root,
                    'user_name': user_name or '',
                    'communication_language': communication_language or 'English',
                    'document_output_language': document_output_language or communication_language or 'English',
                    'user_skill_level': user_skill_level or 'advanced',
                }
                config_path.write_text(yaml.safe_dump(config_payload, sort_keys=False), encoding='utf-8')
                created_paths.append(str(config_path))
        else:
            notes.append('Skipped _bmad/core/config.yaml creation by request.')

        if (root / '_bmad-output').exists() and legacy_output_root != '_bmad-output':
            notes.append('Detected existing _bmad-output alongside configured output_folder; preserve both until manually reconciled.')

        return {
            'project_root': str(root),
            'project_name': canonical_project_name,
            'state_path': str(state_path),
            'notes_path': str(notes_path),
            'config_path': str(config_path) if create_core_config else None,
            'legacy_output_root': str((root / legacy_output_root).resolve()),
            'created_paths': created_paths,
            'preserved_paths': preserved_paths,
            'notes': notes,
        }
