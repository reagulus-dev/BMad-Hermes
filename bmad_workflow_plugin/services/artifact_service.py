from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any, Callable

from bmad_workflow_plugin.registry.loader import RegistryLoader
from bmad_workflow_plugin.registry.models import ArtifactContract
from bmad_workflow_plugin.paths.resolver import PathResolver
from bmad_workflow_plugin.mutations.template_renderer import TemplateRenderer


Factory = Callable[[], Any]


def _factory(module_path: str, object_name: str) -> Factory:
    def _build() -> Any:
        module = import_module(module_path)
        return getattr(module, object_name)()

    return _build


DEFAULT_PARSER_FACTORIES: dict[str, Factory] = {
    'brainstorming_session': _factory(
        'bmad_workflow_plugin.parsers.brainstorming_session_parser', 'BrainstormingSessionParser'
    ),
    'product_brief': _factory(
        'bmad_workflow_plugin.parsers.product_brief_parser', 'ProductBriefParser'
    ),
    'prfaq': _factory('bmad_workflow_plugin.parsers.prfaq_parser', 'PRFAQParser'),
    'prd': _factory('bmad_workflow_plugin.parsers.prd_parser', 'PRD_parser'),
    'prd_validation_report': _factory(
        'bmad_workflow_plugin.parsers.prd_validation_report_parser', 'PRDValidationReportParser'
    ),
    'ux_design': _factory('bmad_workflow_plugin.parsers.ux_design_parser', 'UXDesignParser'),
    'architecture': _factory('bmad_workflow_plugin.parsers.architecture_parser', 'ArchitectureParser'),
    'epics_and_stories': _factory(
        'bmad_workflow_plugin.parsers.epics_and_stories_parser', 'EpicsAndStoriesParser'
    ),
    'project_context': _factory(
        'bmad_workflow_plugin.parsers.project_context_parser', 'ProjectContextParser'
    ),
    'story': _factory('bmad_workflow_plugin.parsers.story_parser', 'StoryParser'),
    'sprint_status': _factory(
        'bmad_workflow_plugin.parsers.sprint_status_parser', 'SprintStatusParser'
    ),
    'review_record': _factory(
        'bmad_workflow_plugin.parsers.review_record_parser', 'ReviewRecordParser'
    ),
    'qa_record': _factory('bmad_workflow_plugin.parsers.qa_record_parser', 'QARecordParser'),
}

DEFAULT_VALIDATOR_FACTORIES: dict[str, Factory] = {
    'brainstorming_session': _factory(
        'bmad_workflow_plugin.validators.brainstorming_session_validator', 'BrainstormingSessionValidator'
    ),
    'product_brief': _factory(
        'bmad_workflow_plugin.validators.product_brief_validator', 'ProductBriefValidator'
    ),
    'prfaq': _factory('bmad_workflow_plugin.validators.prfaq_validator', 'PRFAQValidator'),
    'prd': _factory('bmad_workflow_plugin.validators.prd_validator', 'PRDValidator'),
    'prd_validation_report': _factory(
        'bmad_workflow_plugin.validators.prd_validation_report_validator', 'PRDValidationReportValidator'
    ),
    'ux_design': _factory('bmad_workflow_plugin.validators.ux_design_validator', 'UXDesignValidator'),
    'architecture': _factory(
        'bmad_workflow_plugin.validators.architecture_validator', 'ArchitectureValidator'
    ),
    'epics_and_stories': _factory(
        'bmad_workflow_plugin.validators.epics_and_stories_validator', 'EpicsAndStoriesValidator'
    ),
    'project_context': _factory(
        'bmad_workflow_plugin.validators.project_context_validator', 'ProjectContextValidator'
    ),
    'story': _factory('bmad_workflow_plugin.validators.story_validator', 'StoryValidator'),
    'sprint_status': _factory(
        'bmad_workflow_plugin.validators.sprint_status_validator', 'SprintStatusValidator'
    ),
    'review_record': _factory(
        'bmad_workflow_plugin.validators.review_record_validator', 'ReviewRecordValidator'
    ),
    'qa_record': _factory('bmad_workflow_plugin.validators.qa_record_validator', 'QARecordValidator'),
}

DEFAULT_MUTATOR_FACTORIES: dict[str, Factory] = {
    'brainstorming_session': _factory(
        'bmad_workflow_plugin.mutations.brainstorming_session_mutator', 'BrainstormingSessionMutator'
    ),
    'product_brief': _factory(
        'bmad_workflow_plugin.mutations.product_brief_mutator', 'ProductBriefMutator'
    ),
    'prfaq': _factory('bmad_workflow_plugin.mutations.prfaq_mutator', 'PRFAQMutator'),
    'prd': _factory('bmad_workflow_plugin.mutations.prd_mutator', 'PRDMutator'),
    'prd_validation_report': _factory(
        'bmad_workflow_plugin.mutations.prd_validation_report_mutator', 'PRDValidationReportMutator'
    ),
    'ux_design': _factory('bmad_workflow_plugin.mutations.ux_design_mutator', 'UXDesignMutator'),
    'architecture': _factory(
        'bmad_workflow_plugin.mutations.architecture_mutator', 'ArchitectureMutator'
    ),
    'epics_and_stories': _factory(
        'bmad_workflow_plugin.mutations.epics_and_stories_mutator', 'EpicsAndStoriesMutator'
    ),
    'project_context': _factory(
        'bmad_workflow_plugin.mutations.project_context_mutator', 'ProjectContextMutator'
    ),
    'story': _factory('bmad_workflow_plugin.mutations.story_mutator', 'StoryMutator'),
    'review_record': _factory(
        'bmad_workflow_plugin.mutations.review_record_mutator', 'ReviewRecordMutator'
    ),
    'qa_record': _factory('bmad_workflow_plugin.mutations.qa_record_mutator', 'QARecordMutator'),
}


class ArtifactService:
    def __init__(
        self,
        registry: dict[str, ArtifactContract] | None = None,
        parser_factories: dict[str, Factory] | None = None,
        validator_factories: dict[str, Factory] | None = None,
        mutator_factories: dict[str, Factory] | None = None,
    ) -> None:
        self.registry = registry or RegistryLoader().load_default()
        self._resolver = PathResolver(self.registry)
        self._renderer = TemplateRenderer()

        self._parser_factories = dict(parser_factories or DEFAULT_PARSER_FACTORIES)
        self._validator_factories = dict(validator_factories or DEFAULT_VALIDATOR_FACTORIES)
        self._mutator_factories = dict(mutator_factories or DEFAULT_MUTATOR_FACTORIES)

        self._parsers: dict[str, Any] = {}
        self._validators: dict[str, Any] = {}
        self._mutators: dict[str, Any] = {}

    def _get_component(self, artifact_type: str, cache: dict[str, Any], factories: dict[str, Factory]) -> Any:
        component = cache.get(artifact_type)
        if component is not None:
            return component

        factory = factories.get(artifact_type)
        if factory is None:
            return None

        component = factory()
        cache[artifact_type] = component
        return component

    def _get_parser(self, artifact_type: str) -> Any:
        parser = self._get_component(artifact_type, self._parsers, self._parser_factories)
        if parser is None:
            raise ValueError(f'Unsupported artifact type: {artifact_type}')
        return parser

    def _get_validator(self, artifact_type: str) -> Any:
        return self._get_component(artifact_type, self._validators, self._validator_factories)

    def _get_mutator(self, artifact_type: str) -> Any:
        mutator = self._get_component(artifact_type, self._mutators, self._mutator_factories)
        if mutator is None:
            raise ValueError(f'Artifact type {artifact_type!r} does not support section mutations.')
        return mutator

    def get_contract(self, artifact_type: str) -> ArtifactContract:
        if isinstance(self.registry, dict):
            contract = self.registry.get(artifact_type)
        else:
            contract = self.registry.get_contract(artifact_type)
        if contract is None:
            raise KeyError(f'Unknown artifact type: {artifact_type}')
        return contract

    def read_artifact(self, project_root: str, artifact_type: str, artifact_path: str | None = None) -> dict:
        """
        Read and parse an artifact. Returns a dict with keys:
          doc, contract, validation_result
        """
        contract = self.get_contract(artifact_type)

        if artifact_path:
            path = Path(artifact_path)
            if not path.exists():
                raise FileNotFoundError(f'Artifact path does not exist: {artifact_path}')
        else:
            resolved = self._resolver.resolve_artifact_path(project_root, artifact_type)
            if resolved.path is None:
                raise FileNotFoundError(
                    f'No {artifact_type} artifact found. Candidates: {resolved.candidates}'
                )
            if resolved.ambiguous:
                raise ValueError(f'Ambiguous artifact path for {artifact_type}: {resolved.candidates}')
            path = Path(resolved.path)

        text = path.read_text(encoding='utf-8')
        parser = self._get_parser(artifact_type)
        doc = parser.parse(str(path), text)

        validator = self._get_validator(artifact_type)
        validation = validator.validate(doc, contract) if validator else None

        return {'doc': doc, 'contract': contract, 'validation_result': validation}

    def validate_artifact(self, project_root: str, artifact_type: str, artifact_path: str | None = None) -> dict:
        """Validate an existing artifact against its contract."""
        result = self.read_artifact(project_root, artifact_type, artifact_path)
        return {
            'artifact_type': artifact_type,
            'valid': result['validation_result'].valid,
            'errors': [{'code': e.code, 'message': e.message, 'details': e.details} for e in result['validation_result'].errors],
            'warnings': [{'code': w.code, 'message': w.message, 'details': w.details} for w in result['validation_result'].warnings],
            'parsed_summary': result['validation_result'].parsed_summary,
            'artifact_path': result['doc'].path,
        }

    def create_from_template(
        self, project_root: str, artifact_type: str, template_vars: dict,
        inventory: dict | None = None, destination_path: str | None = None, overwrite: bool = False
    ) -> dict:
        """
        Render a template and write the artifact to the preferred path.
        Returns dict with path and summary.
        """
        contract = self.get_contract(artifact_type)
        templates = contract.raw.get('source_templates', {})
        primary = templates.get('primary', {})
        template_path = primary.get('path')
        if not template_path:
            raise ValueError(f'No template configured for artifact type: {artifact_type}')
        if not Path(template_path).exists():
            raise FileNotFoundError(f'Template file not found: {template_path}')

        vars_full = {**(inventory or {}), **template_vars}
        rendered = self._renderer.render(template_path, vars_full)

        if destination_path:
            dest = Path(destination_path)
        else:
            identity = dict(template_vars)
            dest = Path(self._resolver.build_preferred_path(project_root, artifact_type, identity))

        dest.parent.mkdir(parents=True, exist_ok=True)

        if dest.exists() and not overwrite:
            raise FileExistsError(f'Artifact already exists at {dest}; use overwrite=True to replace')

        dest.write_text(rendered, encoding='utf-8')

        validation_result = None
        try:
            read_result = self.read_artifact(project_root, artifact_type, str(dest))
            validation_result = read_result['validation_result']
        except Exception:
            pass

        return {
            'path': str(dest.resolve()),
            'artifact_type': artifact_type,
            'template_used': template_path,
            'validation_result': validation_result,
        }

    def update_artifact_sections(
        self, project_root: str, artifact_type: str, artifact_path: str, workflow_id: str, operations: list[dict]
    ) -> dict:
        """
        Apply section-level mutations to any registered artifact type.
        Transaction: read -> mutate -> validate -> write.
        Returns dict with updated, path, validation_result, notes.
        """
        mutator = self._get_mutator(artifact_type)

        read_result = self.read_artifact(project_root, artifact_type, artifact_path)
        doc = read_result['doc']
        contract = read_result['contract']

        updated_doc = mutator.apply_operations(doc, workflow_id, operations, contract)

        validator = self._get_validator(artifact_type)
        validation = validator.validate(updated_doc, contract) if validator else None

        Path(updated_doc.path).write_text(updated_doc.raw_text, encoding='utf-8')

        label = getattr(doc, 'story_key', None) or getattr(doc, 'story_key', 'artifact')

        return {
            'updated': True,
            'path': updated_doc.path,
            'validation_result': validation,
            'notes': [f'Applied {len(operations)} operation(s) to {artifact_type} {label}'],
        }

    def update_story_sections(
        self, project_root: str, artifact_path: str, workflow_id: str, operations: list[dict]
    ) -> dict:
        return self.update_artifact_sections(
            project_root, 'story', artifact_path, workflow_id, operations
        )
