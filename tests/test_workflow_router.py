from pathlib import Path

from bmad_workflow_plugin.registry.workflow_loader import WorkflowRegistryLoader
from bmad_workflow_plugin.routing.workflow_router import WorkflowRouter


SPRINT_STATUS_BACKLOG = """generated: now
project: demo
project_key: DEMO
tracking_system: file-system
story_location: _bmad/artifacts/stories
development_status:
  epic-1: in-progress
  1-1-done-story: done
  1-2-next-story: backlog
"""

SPRINT_STATUS_RETRO = """generated: now
project: demo
project_key: DEMO
tracking_system: file-system
story_location: _bmad/artifacts/stories
development_status:
  epic-1: in-progress
  1-1-story-a: done
  1-2-story-b: done
  epic-1-retrospective: optional
"""

SPRINT_STATUS_REAL_EXPORT = """metadata:
  project: LapseLess
  generated: 2026-03-20 21:10:00+00:00
sprints:
- sprint: 1
  stories:
  - id: 1.1
    title: User Registration with Email
    status: dev_complete
  - id: 1.7
    title: Session Persistence
    status: spec_created
"""


def test_workflow_router_missing_state_routes_to_project_init(tmp_path: Path) -> None:
    decision = WorkflowRouter().next_workflow(str(tmp_path))
    assert decision.next_workflow_id == 'bmad-project-init'
    assert decision.recommended_skill == 'bmad-project-init'


def test_workflow_registry_aliases_resolve() -> None:
    loader = WorkflowRegistryLoader()

    assert loader.get('project-init').workflow_id == 'bmad-project-init'
    assert loader.get('sprint-planning').workflow_id == 'bmad-sprint-planning'
    assert loader.get('create-story').workflow_id == 'bmad-create-story'
    assert loader.get('retrospective').workflow_id == 'bmad-retrospective'


def test_workflow_router_without_sprint_status_routes_to_bmad_sprint_planning(tmp_path: Path) -> None:
    state_dir = tmp_path / '_bmad'
    state_dir.mkdir(parents=True)
    (state_dir / 'state.json').write_text('{"schema_version":"2.0","workflow_status":"idle","current_phase":"implementation","updated_at":"2099-01-01T00:00:00Z"}', encoding='utf-8')

    decision = WorkflowRouter().next_workflow(str(tmp_path))

    assert decision.next_workflow_id == 'bmad-sprint-planning'
    assert decision.recommended_skill == 'bmad-sprint-planning'


def test_workflow_router_done_story_with_next_backlog_routes_to_bmad_create_story(tmp_path: Path) -> None:
    bmad = tmp_path / '_bmad'
    bmad.mkdir(parents=True)
    (bmad / 'state.json').write_text('{"schema_version":"2.0","workflow_status":"idle","current_phase":"implementation","current_story":"1-1-done-story","updated_at":"2099-01-01T00:00:00Z"}', encoding='utf-8')

    sprint_path = tmp_path / '_bmad' / 'artifacts' / 'state' / 'sprint-status.yaml'
    sprint_path.parent.mkdir(parents=True, exist_ok=True)
    sprint_path.write_text(SPRINT_STATUS_BACKLOG, encoding='utf-8')

    decision = WorkflowRouter().next_workflow(str(tmp_path), target_story_key='1-1-done-story')

    assert decision.next_workflow_id == 'bmad-create-story'
    assert decision.recommended_skill == 'bmad-create-story'
    assert decision.target_story_key == '1-2-next-story'


def test_workflow_router_done_epic_with_optional_retro_routes_to_bmad_retrospective(tmp_path: Path) -> None:
    bmad = tmp_path / '_bmad'
    bmad.mkdir(parents=True)
    (bmad / 'state.json').write_text('{"schema_version":"2.0","workflow_status":"idle","current_phase":"implementation","current_story":"1-1-story-a","updated_at":"2099-01-01T00:00:00Z"}', encoding='utf-8')

    sprint_path = tmp_path / '_bmad' / 'artifacts' / 'state' / 'sprint-status.yaml'
    sprint_path.parent.mkdir(parents=True, exist_ok=True)
    sprint_path.write_text(SPRINT_STATUS_RETRO, encoding='utf-8')

    decision = WorkflowRouter().next_workflow(str(tmp_path), target_story_key='1-1-story-a')

    assert decision.next_workflow_id == 'bmad-retrospective'
    assert decision.recommended_skill == 'bmad-retrospective'
    assert decision.target_story_key == '1-1-story-a'


def test_workflow_router_routes_real_export_nested_sprint_layout_to_create_story(tmp_path: Path) -> None:
    bmad = tmp_path / '_bmad'
    bmad.mkdir(parents=True)
    (bmad / 'state.json').write_text('{"schema_version":"2.0","workflow_status":"idle","current_phase":"implementation","updated_at":"2099-01-01T00:00:00Z"}', encoding='utf-8')
    (bmad / 'config.yaml').write_text('project_name: LapseLess\noutput_folder: _bmad-output\n', encoding='utf-8')

    sprint_path = tmp_path / '_bmad-output' / 'implementation-artifacts' / 'sprint-status.yaml'
    sprint_path.parent.mkdir(parents=True, exist_ok=True)
    sprint_path.write_text(SPRINT_STATUS_REAL_EXPORT, encoding='utf-8')

    decision = WorkflowRouter().next_workflow(str(tmp_path))

    assert decision.next_workflow_id == 'bmad-create-story'
    assert decision.recommended_skill == 'bmad-create-story'
    assert decision.target_story_key == '1-7'


def test_workflow_router_lazy_loads_only_needed_components_for_missing_state(tmp_path: Path) -> None:
    counts = {'path_resolver': 0, 'state_reader': 0, 'state_normalizer': 0, 'sprint_parser': 0}

    class DummyStateReader:
        def read(self, project_root: str):
            return None

    class DummyNormalizedState:
        state_regime = 'missing'
        normalized_state = {}

    class DummyStateNormalizer:
        def normalize(self, project_root: str, raw_state):
            return DummyNormalizedState()

    class DummyPathResolver:
        def resolve_artifact_path(self, project_root: str, artifact_type: str):
            raise AssertionError('PathResolver should not be created for missing-state routing')

    class DummySprintParser:
        def parse(self, path: str, text: str):
            raise AssertionError('SprintStatusParser should not be created for missing-state routing')

    def build_path_resolver():
        counts['path_resolver'] += 1
        return DummyPathResolver()

    def build_state_reader():
        counts['state_reader'] += 1
        return DummyStateReader()

    def build_state_normalizer():
        counts['state_normalizer'] += 1
        return DummyStateNormalizer()

    def build_sprint_parser():
        counts['sprint_parser'] += 1
        return DummySprintParser()

    router = WorkflowRouter(
        path_resolver_factory=build_path_resolver,
        state_reader_factory=build_state_reader,
        state_normalizer_factory=build_state_normalizer,
        sprint_status_parser_factory=build_sprint_parser,
    )

    assert counts == {'path_resolver': 0, 'state_reader': 0, 'state_normalizer': 0, 'sprint_parser': 0}

    decision = router.next_workflow(str(tmp_path))

    assert decision.next_workflow_id == 'bmad-project-init'
    assert decision.recommended_skill == 'bmad-project-init'
    assert counts == {'path_resolver': 0, 'state_reader': 1, 'state_normalizer': 1, 'sprint_parser': 0}
