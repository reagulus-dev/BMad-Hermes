from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from bmad_workflow_plugin.parsers.sprint_status_parser import SprintStatusParser
from bmad_workflow_plugin.paths.resolver import PathResolver
from bmad_workflow_plugin.state.state_normalizer import StateNormalizer
from bmad_workflow_plugin.state.state_reader import StateReader
from bmad_workflow_plugin.state.state_writer import StateWriter


class StateMigrationService:
    def __init__(self, registry) -> None:
        self.registry = registry
        self._reader = StateReader()
        self._writer = StateWriter()
        self._normalizer = StateNormalizer()
        self._resolver = PathResolver(registry)
        self._sprint_parser = SprintStatusParser()

    def migrate(self, project_root: str) -> dict:
        root = Path(project_root).resolve()
        state_path = root / '_bmad' / 'state.json'
        raw_state = self._reader.read(str(root))
        if raw_state is None:
            raise FileNotFoundError(f'No legacy BMad state or config found under {root}/_bmad')

        backup_path = self._backup_state_file(state_path)
        completed_workflows = raw_state.get('completedWorkflows', []) or []
        last_artifacts, blockers, notes = self._collect_artifact_evidence(str(root), raw_state)

        current_story = raw_state.get('current_story') or self._current_story_from_sprint(str(root))
        workflow_status = raw_state.get('workflow_status') or self._infer_workflow_status(raw_state)
        current_phase = raw_state.get('current_phase') or raw_state.get('currentPhase') or self._infer_current_phase(last_artifacts)
        project_name = (
            raw_state.get('project_name')
            or raw_state.get('projectName')
            or (raw_state.get('__bmad_config__', {}) or {}).get('project_name')
            or root.name
        )
        created_at = raw_state.get('created_at') or raw_state.get('createdAt') or self._now_iso()
        now = self._now_iso()

        patch = {
            'schema_version': '2.0',
            'persona': 'BMad',
            'method': 'bmad-hermes',
            'project_name': project_name,
            'project_root': str(root),
            'created_at': created_at,
            'current_phase': current_phase,
            'workflow_status': workflow_status,
            'active_workflow': raw_state.get('active_workflow') or self._normalize_active_workflow(raw_state.get('activeWorkflow')),
            'current_epic': raw_state.get('current_epic'),
            'current_story': current_story,
            'current_sprint': raw_state.get('current_sprint'),
            'blockers': blockers,
            'last_artifacts': last_artifacts,
            'last_review_summary': self._review_summary(raw_state, current_story, state_path.exists()),
            'last_evidence_path': last_artifacts[-1] if last_artifacts else None,
            'next_recommended_workflows': ['bmad-state-check'],
            'state_check': {
                'last_checked_at': now,
                'trust_level': 'partial',
                'notes': notes,
            },
            'legacy_bmad': {
                'preserved': True,
                'completed_workflows': completed_workflows,
            },
        }

        self._writer.write_patch(str(root), patch)
        normalized = self._normalizer.normalize(str(root), self._reader.read(str(root)))

        return {
            'project_root': str(root),
            'state_path': str(state_path),
            'backup_path': backup_path,
            'legacy_history_preserved': len(completed_workflows) == len((raw_state.get('completedWorkflows', []) or [])),
            'legacy_history_count': len(completed_workflows),
            'added_keys': sorted(patch.keys()),
            'state_regime': normalized.state_regime,
            'trust_level': normalized.trust_level,
            'blockers': blockers,
            'last_artifacts': last_artifacts,
            'recommended_next_workflow': 'bmad-state-check',
            'notes': notes,
        }

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    def _backup_state_file(self, state_path: Path) -> str | None:
        if not state_path.exists():
            return None
        stamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H%M%SZ')
        backup_path = state_path.with_name(f'state.pre-alice-backup-{stamp}.json')
        shutil.copy2(state_path, backup_path)
        return str(backup_path)

    def _collect_artifact_evidence(self, project_root: str, raw_state: dict) -> tuple[list[str], list[str], list[str]]:
        artifact_types = [
            'product_brief',
            'prfaq',
            'prd',
            'prd_validation_report',
            'ux_design',
            'architecture',
            'epics_and_stories',
            'project_context',
            'sprint_status',
        ]
        story_key = raw_state.get('current_story') or raw_state.get('currentStory')
        if story_key:
            artifact_types.append('story')

        last_artifacts: list[str] = []
        blockers: list[str] = []
        notes: list[str] = []

        for artifact_type in artifact_types:
            identity = {'story_key': story_key} if artifact_type == 'story' and story_key else None
            resolved = self._resolver.resolve_artifact_path(project_root, artifact_type, identity)
            if resolved.ambiguous:
                blockers.append(f'ambiguous {artifact_type} artifacts')
                notes.append(f'{artifact_type} resolved ambiguously: ' + ', '.join(resolved.candidates[:4]))
                continue
            if resolved.path:
                last_artifacts.append(resolved.path)

        if not self._state_path_exists(project_root):
            notes.append('Seeded normalized state from legacy BMad config/export layout because _bmad/state.json was missing.')
        else:
            notes.append('Preserved legacy _bmad/state.json and added normalized BMad-managed live-state fields.')

        if not any(path.endswith('sprint-status.yaml') for path in last_artifacts):
            notes.append('No sprint-status artifact resolved during migration; post-migration state-check should confirm execution focus.')

        return last_artifacts, blockers, notes

    def _current_story_from_sprint(self, project_root: str) -> str | None:
        resolved = self._resolver.resolve_artifact_path(project_root, 'sprint_status')
        if resolved.path is None or resolved.ambiguous:
            return None
        sprint_text = Path(resolved.path).read_text(encoding='utf-8')
        sprint_doc = self._sprint_parser.parse(resolved.path, sprint_text)
        for desired in ('review', 'in-progress', 'ready-for-dev', 'backlog', 'blocked', 'done'):
            for entry in sprint_doc.development_status:
                if entry.entry_type == 'story' and entry.status == desired:
                    return entry.key
        return None

    @staticmethod
    def _infer_workflow_status(raw_state: dict) -> str:
        active = raw_state.get('active_workflow')
        if active not in (None, {}, ''):
            return 'in_progress'
        active = raw_state.get('activeWorkflow')
        if active not in (None, {}, ''):
            return 'in_progress'
        return 'idle'

    @staticmethod
    def _normalize_active_workflow(active_workflow):
        if active_workflow in ({}, ''):
            return None
        return active_workflow

    @staticmethod
    def _infer_current_phase(last_artifacts: list[str]) -> str | None:
        lowered = [path.lower() for path in last_artifacts]
        if any('implementation-artifacts' in path or 'sprint-status' in path or '/stories/' in path for path in lowered):
            return 'implementation'
        if any('architecture' in path or 'epics-and-stories' in path or 'project-context' in path for path in lowered):
            return 'solutioning'
        if any('/prds/' in path or 'prd' in path or 'ux-design' in path for path in lowered):
            return 'planning'
        if any('product-brief' in path or 'prfaq' in path or 'brainstorm' in path for path in lowered):
            return 'analysis'
        return None

    @staticmethod
    def _review_summary(raw_state: dict, current_story: str | None, had_state_file: bool) -> str:
        if had_state_file:
            prefix = 'Migrated legacy BMad state into BMad-compatible live state.'
        else:
            prefix = 'Created BMad-compatible live state from legacy BMad config/export layout.'
        if current_story:
            return f'{prefix} Current inferred story: {current_story}.'
        return prefix

    @staticmethod
    def _state_path_exists(project_root: str) -> bool:
        return (Path(project_root) / '_bmad' / 'state.json').exists()