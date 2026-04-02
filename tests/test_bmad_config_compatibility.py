from __future__ import annotations

from pathlib import Path

from bmad_workflow_plugin.paths.resolver import PathResolver
from bmad_workflow_plugin.registry.loader import RegistryLoader
from bmad_workflow_plugin.services.state_service import StateService


def _write_bmad_config(project_root: Path, *, core: bool = True, **overrides) -> Path:
    config = {
        'project_name': 'acme-app',
        'user_name': 'reagulus',
        'communication_language': 'English',
        'document_output_language': 'English',
        'user_skill_level': 'advanced',
        'output_folder': '_bmad-output',
    }
    config.update(overrides)
    path = project_root / '_bmad' / ('core/config.yaml' if core else 'config.yaml')
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f'{key}: {value}' for key, value in config.items()]
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return path


def test_state_service_marks_config_only_project_as_legacy_only(tmp_path: Path) -> None:
    _write_bmad_config(tmp_path, project_name='legacy-bmad', output_folder='legacy-docs')

    state = StateService(registry=RegistryLoader().load_default()).get_state(str(tmp_path))

    assert state.state_regime == 'legacy_only'
    assert state.normalized_state['bmad_config']['project_name'] == 'legacy-bmad'
    assert state.normalized_state['bmad_config']['output_folder'] == 'legacy-docs'


def test_state_service_reads_root_level_bmad_config_from_real_export_layout(tmp_path: Path) -> None:
    _write_bmad_config(tmp_path, core=False, project_name='exported-bmad', output_folder='_bmad-output')

    state = StateService(registry=RegistryLoader().load_default()).get_state(str(tmp_path))

    assert state.state_regime == 'legacy_only'
    assert state.normalized_state['bmad_config']['project_name'] == 'exported-bmad'
    assert state.normalized_state['bmad_config']['output_folder'] == '_bmad-output'


def test_build_preferred_path_uses_project_name_from_bmad_config(tmp_path: Path) -> None:
    _write_bmad_config(tmp_path, project_name='config-driven-project')
    resolver = PathResolver(RegistryLoader().load_default())

    path = resolver.build_preferred_path(str(tmp_path), 'prd', {})

    assert path.endswith('/_bmad/artifacts/planning/prds/config-driven-project/prd.md')


def test_resolve_legacy_path_uses_output_folder_from_bmad_config(tmp_path: Path) -> None:
    _write_bmad_config(tmp_path, output_folder='docs-output')
    resolver = PathResolver(RegistryLoader().load_default())

    legacy_path = tmp_path / 'docs-output' / 'implementation-artifacts' / 'sprint-status.yaml'
    legacy_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_path.write_text('generated: now\nproject: Demo\nproject_key: demo\ntracking_system: bmad\nstory_location: implementation-artifacts\ndevelopment_status: []\n', encoding='utf-8')

    result = resolver.resolve_artifact_path(str(tmp_path), 'sprint_status')

    assert result.path == str(legacy_path)
    assert result.source_kind == 'legacy_compatible'
    assert result.ambiguous is False


def test_resolve_legacy_project_artifact_without_identity_uses_config_and_glob(tmp_path: Path) -> None:
    _write_bmad_config(tmp_path, project_name='acme-app', output_folder='legacy-output')
    resolver = PathResolver(RegistryLoader().load_default())

    legacy_prd = tmp_path / 'legacy-output' / 'planning-artifacts' / 'prds' / 'acme-app' / 'prd.md'
    legacy_prd.parent.mkdir(parents=True, exist_ok=True)
    legacy_prd.write_text('# PRD\n', encoding='utf-8')

    result = resolver.resolve_artifact_path(str(tmp_path), 'prd')

    assert result.path == str(legacy_prd)
    assert result.source_kind == 'legacy_compatible'
    assert result.ambiguous is False


def test_resolve_real_export_legacy_planning_paths(tmp_path: Path) -> None:
    _write_bmad_config(tmp_path, core=False, project_name='LapseLess', output_folder='_bmad-output')
    resolver = PathResolver(RegistryLoader().load_default())

    product_brief = tmp_path / '_bmad-output' / 'planning-artifacts' / 'product-brief-LapseLess-2026-03-20.md'
    prd = tmp_path / '_bmad-output' / 'planning-artifacts' / 'prd-v2.md'
    prd_validation = tmp_path / '_bmad-output' / 'planning-artifacts' / 'prd-validation-report-v2.md'
    architecture = tmp_path / '_bmad-output' / 'planning-artifacts' / 'architecture.md'
    ux_design = tmp_path / '_bmad-output' / 'planning-artifacts' / 'ux-design-specification.md'
    epics = tmp_path / '_bmad-output' / 'planning-artifacts' / 'epics-and-stories-LapseLess.md'
    for artifact in (product_brief, prd, prd_validation, architecture, ux_design, epics):
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text('# artifact\n', encoding='utf-8')

    assert resolver.resolve_artifact_path(str(tmp_path), 'product_brief').path == str(product_brief)
    assert resolver.resolve_artifact_path(str(tmp_path), 'prd').path == str(prd)
    assert resolver.resolve_artifact_path(str(tmp_path), 'prd_validation_report').path == str(prd_validation)
    assert resolver.resolve_artifact_path(str(tmp_path), 'architecture').path == str(architecture)
    assert resolver.resolve_artifact_path(str(tmp_path), 'ux_design').path == str(ux_design)
    assert resolver.resolve_artifact_path(str(tmp_path), 'epics_and_stories').path == str(epics)


def test_resolve_real_export_story_path_with_short_story_key(tmp_path: Path) -> None:
    _write_bmad_config(tmp_path, core=False, project_name='ProofKey', output_folder='_bmad-output')
    resolver = PathResolver(RegistryLoader().load_default())

    story_path = tmp_path / '_bmad-output' / 'implementation-artifacts' / 'stories' / 'story-1-1-create-property-record.md'
    story_path.parent.mkdir(parents=True, exist_ok=True)
    story_path.write_text('# Story 1.1: Create Property Record\n', encoding='utf-8')

    result = resolver.resolve_artifact_path(str(tmp_path), 'story', {'story_key': '1-1'})

    assert result.path == str(story_path)
    assert result.source_kind == 'legacy_compatible'
    assert result.ambiguous is False
