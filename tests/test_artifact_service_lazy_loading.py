from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from bmad_workflow_plugin.registry.loader import RegistryLoader
from bmad_workflow_plugin.services.artifact_service import ArtifactService


@dataclass
class DummyValidationResult:
    valid: bool = True
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    parsed_summary: dict = field(default_factory=dict)


@dataclass
class DummyDoc:
    path: str
    raw_text: str
    story_key: str = 'story-1'


class DummyParser:
    def parse(self, path: str, text: str) -> DummyDoc:
        return DummyDoc(path=path, raw_text=text)


class DummyValidator:
    def validate(self, doc: DummyDoc, contract) -> DummyValidationResult:
        return DummyValidationResult(parsed_summary={'path': doc.path})


class DummyMutator:
    def apply_operations(self, doc: DummyDoc, workflow_id: str, operations: list[dict], contract) -> DummyDoc:
        return DummyDoc(path=doc.path, raw_text=doc.raw_text + '\n# updated\n', story_key=doc.story_key)


def test_artifact_service_lazy_loads_and_caches_components(tmp_path: Path) -> None:
    registry = RegistryLoader().load_default()
    artifact_path = tmp_path / 'story.md'
    artifact_path.write_text('# Story\n', encoding='utf-8')

    counts = {'parser': 0, 'validator': 0, 'mutator': 0}

    def build_parser() -> DummyParser:
        counts['parser'] += 1
        return DummyParser()

    def build_validator() -> DummyValidator:
        counts['validator'] += 1
        return DummyValidator()

    def build_mutator() -> DummyMutator:
        counts['mutator'] += 1
        return DummyMutator()

    service = ArtifactService(
        registry=registry,
        parser_factories={'story': build_parser},
        validator_factories={'story': build_validator},
        mutator_factories={'story': build_mutator},
    )

    assert counts == {'parser': 0, 'validator': 0, 'mutator': 0}
    assert service._parsers == {}
    assert service._validators == {}
    assert service._mutators == {}

    first_read = service.read_artifact(str(tmp_path), 'story', str(artifact_path))

    assert first_read['doc'].path == str(artifact_path)
    assert counts == {'parser': 1, 'validator': 1, 'mutator': 0}
    assert set(service._parsers.keys()) == {'story'}
    assert set(service._validators.keys()) == {'story'}
    assert service._mutators == {}

    second_read = service.read_artifact(str(tmp_path), 'story', str(artifact_path))

    assert second_read['doc'].path == str(artifact_path)
    assert counts == {'parser': 1, 'validator': 1, 'mutator': 0}

    update_result = service.update_artifact_sections(
        str(tmp_path),
        'story',
        str(artifact_path),
        'bmad-dev-story',
        [{'op': 'replace_section', 'section': 'Notes', 'content': 'Updated'}],
    )

    assert update_result['updated'] is True
    assert counts == {'parser': 1, 'validator': 1, 'mutator': 1}
    assert set(service._mutators.keys()) == {'story'}
    assert artifact_path.read_text(encoding='utf-8').endswith('# updated\n')
