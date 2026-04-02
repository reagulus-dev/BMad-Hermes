from __future__ import annotations

from datetime import datetime, timezone

from bmad_workflow_plugin.schemas.artifact_models import NormalizedState


class StateNormalizer:
    def normalize(self, project_root: str, raw_state: dict | None) -> NormalizedState:
        if raw_state is None:
            return NormalizedState(
                project_root=project_root,
                state_regime='missing',
                trust_level='low',
                normalized_state={
                    'schema_version': None,
                    'workflow_status': None,
                    'current_phase': None,
                    'current_story': None,
                    'current_epic': None,
                    'current_sprint': None,
                    'blockers': [],
                    'last_artifacts': [],
                    'last_review_summary': None,
                    'last_evidence_path': None,
                    'next_recommended_workflows': [],
                    'bmad_config': {},
                    'updated_at': None,
                },
            )

        has_snake = any(k in raw_state for k in ('schema_version', 'workflow_status', 'current_phase', 'current_story', 'state_check'))
        has_legacy = any(k in raw_state for k in ('projectName', 'projectPath', 'createdAt', 'currentPhase', 'activeWorkflow', 'completedWorkflows'))

        if has_snake and has_legacy:
            regime = 'partially_normalized'
        elif has_snake:
            regime = 'normalized_ready'
        elif has_legacy:
            regime = 'legacy_only'
        else:
            regime = 'partially_normalized'

        trust_level = self._trust_level(raw_state, regime)
        bmad_config = raw_state.get('__bmad_config__', {}) or {}
        normalized = {
            'schema_version': raw_state.get('schema_version'),
            'workflow_status': raw_state.get('workflow_status'),
            'current_phase': raw_state.get('current_phase'),
            'current_story': raw_state.get('current_story'),
            'current_epic': raw_state.get('current_epic'),
            'current_sprint': raw_state.get('current_sprint'),
            'blockers': raw_state.get('blockers', []) or [],
            'last_artifacts': raw_state.get('last_artifacts', []) or [],
            'last_review_summary': raw_state.get('last_review_summary'),
            'last_evidence_path': raw_state.get('last_evidence_path'),
            'next_recommended_workflows': raw_state.get('next_recommended_workflows', []) or [],
            'bmad_config': {
                'project_name': bmad_config.get('project_name'),
                'user_name': bmad_config.get('user_name'),
                'communication_language': bmad_config.get('communication_language'),
                'document_output_language': bmad_config.get('document_output_language'),
                'user_skill_level': bmad_config.get('user_skill_level'),
                'output_folder': bmad_config.get('output_folder'),
            },
            'updated_at': raw_state.get('updated_at'),
        }

        if not has_snake and has_legacy:
            normalized['current_phase'] = raw_state.get('currentPhase')
            normalized['workflow_status'] = 'idle' if raw_state.get('activeWorkflow') in (None, {}) else 'in_progress'
            normalized['current_story'] = None
            normalized['next_recommended_workflows'] = []

        if regime == 'normalized_ready' and self._looks_stale(raw_state):
            regime = 'normalized_stale'

        return NormalizedState(
            project_root=project_root,
            state_regime=regime,
            trust_level=trust_level,
            normalized_state=normalized,
        )

    @staticmethod
    def _trust_level(raw_state: dict, regime: str) -> str:
        if regime == 'missing':
            return 'low'
        state_check = raw_state.get('state_check', {}) or {}
        trust = state_check.get('trust_level')
        if trust in {'high', 'partial', 'low'}:
            return trust
        if regime == 'normalized_ready':
            return 'partial'
        if regime == 'normalized_stale':
            return 'partial'
        return 'low'

    @staticmethod
    def _looks_stale(raw_state: dict) -> bool:
        updated_at = raw_state.get('updated_at')
        if not updated_at:
            return True
        try:
            ts = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        except Exception:
            return True
        now = datetime.now(timezone.utc)
        return (now - ts).days > 30
