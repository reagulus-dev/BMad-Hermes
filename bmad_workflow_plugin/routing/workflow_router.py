from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any, Callable

from bmad_workflow_plugin.registry.loader import RegistryLoader as ArtifactRegistryLoader
from bmad_workflow_plugin.registry.workflow_loader import WorkflowRegistryLoader
from bmad_workflow_plugin.registry.workflow_models import WorkflowEntry
from bmad_workflow_plugin.schemas.workflow_models import RoutingDecision


Factory = Callable[[], Any]


def _factory(module_path: str, object_name: str) -> Factory:
    def _build() -> Any:
        module = import_module(module_path)
        return getattr(module, object_name)()

    return _build


class WorkflowRouter:
    def __init__(
        self,
        registry_loader: WorkflowRegistryLoader | None = None,
        path_resolver_factory: Factory | None = None,
        state_reader_factory: Factory | None = None,
        state_normalizer_factory: Factory | None = None,
        sprint_status_parser_factory: Factory | None = None,
    ) -> None:
        self.registry_loader = registry_loader or WorkflowRegistryLoader()

        self._path_resolver_factory = path_resolver_factory or self._default_path_resolver_factory
        self._state_reader_factory = state_reader_factory or _factory(
            'bmad_workflow_plugin.state.state_reader', 'StateReader'
        )
        self._state_normalizer_factory = state_normalizer_factory or _factory(
            'bmad_workflow_plugin.state.state_normalizer', 'StateNormalizer'
        )
        self._sprint_status_parser_factory = sprint_status_parser_factory or _factory(
            'bmad_workflow_plugin.parsers.sprint_status_parser', 'SprintStatusParser'
        )

        self._path_resolver = None
        self._state_reader = None
        self._state_normalizer = None
        self._sprint_status_parser = None

    @staticmethod
    def _default_path_resolver_factory() -> Any:
        from bmad_workflow_plugin.paths.resolver import PathResolver

        artifact_registry = ArtifactRegistryLoader().load()
        return PathResolver(artifact_registry)

    @property
    def _registry(self):
        return self.registry_loader.load()

    def _get_path_resolver(self):
        if self._path_resolver is None:
            self._path_resolver = self._path_resolver_factory()
        return self._path_resolver

    def _get_state_reader(self):
        if self._state_reader is None:
            self._state_reader = self._state_reader_factory()
        return self._state_reader

    def _get_state_normalizer(self):
        if self._state_normalizer is None:
            self._state_normalizer = self._state_normalizer_factory()
        return self._state_normalizer

    def _get_sprint_status_parser(self):
        if self._sprint_status_parser is None:
            self._sprint_status_parser = self._sprint_status_parser_factory()
        return self._sprint_status_parser

    def next_workflow(self, project_root: str, target_story_key: str | None = None) -> RoutingDecision:
        """Determine the next workflow given the current project state."""
        raw_state = self._get_state_reader().read(project_root)
        norm = self._get_state_normalizer().normalize(project_root, raw_state)

        decision = self._route_state_regime(norm, target_story_key)
        if decision is not None:
            return decision

        sprint_resolved = self._get_path_resolver().resolve_artifact_path(project_root, 'sprint_status')
        if sprint_resolved.path is None:
            return self._decision(
                'bmad-sprint-planning',
                'bmad-sprint-planning',
                'No sprint-status artifact found.',
                False,
                [],
                target_story_key,
            )
        if sprint_resolved.ambiguous:
            return self._decision(
                'state-check', 'bmad-state-check',
                'Multiple sprint-status artifacts found; manual resolution needed.',
                True, ['ambiguous sprint_status artifacts'], target_story_key,
            )

        sprint_text = Path(sprint_resolved.path).read_text(encoding='utf-8')
        sprint_doc = self._get_sprint_status_parser().parse(sprint_resolved.path, sprint_text)

        chosen_story_key = target_story_key or norm.normalized_state.get('current_story')
        if not chosen_story_key:
            chosen_story_key = self._first_actionable_story(sprint_doc)

        if not chosen_story_key:
            return self._decision(
                'bmad-sprint-status', 'bmad-sprint-status',
                'No actionable story found in sprint status.',
                False, [], target_story_key,
            )

        story_status = self._story_status_from_sprint(sprint_doc, chosen_story_key)

        if story_status:
            decision = self._route_by_story_status(story_status, chosen_story_key, sprint_doc)
            if decision is not None:
                return decision

        return self._decision(
            'bmad-state-check', 'bmad-state-check',
            'Could not determine a clear next workflow from current state.',
            False, [], chosen_story_key,
        )

    def _route_state_regime(self, norm, target_story_key):
        """Handle missing/legacy/partially-normalized state regimes."""
        if norm.state_regime == 'missing':
            return self._decision(
                'bmad-project-init', 'bmad-project-init',
                'No _bmad/state.json found.', False, [], target_story_key,
            )
        if norm.state_regime == 'legacy_only':
            return self._decision(
                'bmad-state-migration', 'bmad-state-migration',
                'Legacy-only BMad state detected.', False, [], target_story_key,
            )
        if norm.state_regime == 'partially_normalized':
            return self._decision(
                'bmad-state-check', 'bmad-state-check',
                'State is only partially normalized.', False, [], target_story_key,
            )
        return None

    def _route_by_story_status(
        self, story_status: str, story_key: str, sprint_doc,
    ) -> RoutingDecision | None:
        """Use the registry to find a workflow matching the story status."""
        candidates = self.registry_loader.get_workflows_for_status(story_status)
        if not candidates:
            return None

        bmad_candidates = [w for w in candidates if w.recommended_skill.startswith('bmad-')]
        primary = (bmad_candidates or candidates)[0]

        reason = f'Story {story_key} has status "{story_status}".'
        blocked = story_status == 'blocked'
        blockers = ['story blocked'] if blocked else []

        if story_status == 'done':
            if self._epic_complete_and_retro_optional(sprint_doc, story_key):
                return self._decision(
                    'bmad-retrospective', 'bmad-retrospective',
                    f'Epic for {story_key} appears complete; retrospective is next.',
                    False, [], story_key,
                )
            next_story = self._first_actionable_story(sprint_doc)
            if next_story and next_story != story_key:
                return self._decision(
                    'bmad-create-story', 'bmad-create-story',
                    f'Current story done; next actionable story is {next_story}.',
                    False, [], next_story,
                )
            return self._decision(
                'bmad-state-check', 'bmad-state-check',
                'Current story is done and no clear next story was inferred.',
                False, [], story_key,
            )

        return self._decision(
            primary.workflow_id,
            primary.recommended_skill,
            reason,
            blocked,
            blockers,
            story_key,
            phase=primary.phase,
        )

    def get_workflow(self, workflow_id: str) -> WorkflowEntry | None:
        """Look up a workflow by ID or alias."""
        return self.registry_loader.get(workflow_id)

    def list_workflows_by_phase(self, phase: str) -> list[WorkflowEntry]:
        return self.registry_loader.by_phase(phase)

    def all_workflows(self) -> list[WorkflowEntry]:
        return self.registry_loader.all_workflows()

    @staticmethod
    def _decision(
        next_workflow_id: str,
        recommended_skill: str,
        reason: str,
        blocked: bool,
        blockers: list[str],
        target_story_key: str | None = None,
        phase: str | None = None,
    ) -> RoutingDecision:
        return RoutingDecision(
            next_workflow_id=next_workflow_id,
            recommended_skill=recommended_skill,
            reason=reason,
            blocked=blocked,
            blockers=blockers,
            target_story_key=target_story_key,
            phase=phase,
        )

    @staticmethod
    def _story_status_from_sprint(sprint_doc, story_key: str) -> str | None:
        for entry in sprint_doc.development_status:
            if entry.key == story_key:
                return entry.status
        return None

    @staticmethod
    def _first_actionable_story(sprint_doc) -> str | None:
        for desired in ('backlog', 'ready-for-dev', 'in-progress', 'review', 'blocked'):
            for entry in sprint_doc.development_status:
                if entry.entry_type == 'story' and entry.status == desired:
                    return entry.key
        return None

    @staticmethod
    def _epic_complete_and_retro_optional(sprint_doc, story_key: str) -> bool:
        try:
            epic_prefix = story_key.split('-')[0]
        except Exception:
            return False
        story_entries = [
            e for e in sprint_doc.development_status
            if e.entry_type == 'story' and e.key.startswith(f'{epic_prefix}-')
        ]
        if not story_entries or any(e.status != 'done' for e in story_entries):
            return False
        retro_key = f'epic-{epic_prefix}-retrospective'
        retro = next((e for e in sprint_doc.development_status if e.key == retro_key), None)
        return retro is not None and retro.status == 'optional'
