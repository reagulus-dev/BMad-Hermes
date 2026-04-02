from bmad_workflow_plugin.registry.loader import RegistryLoader
from bmad_workflow_plugin.parsers.sprint_status_parser import SprintStatusParser
from bmad_workflow_plugin.validators.sprint_status_validator import SprintStatusValidator


def test_sprint_status_validator_accepts_basic_valid_doc() -> None:
    registry = RegistryLoader().load_default()
    contract = registry['sprint_status']
    text = """generated: now
project: demo
project_key: NOKEY
tracking_system: file-system
story_location: _bmad/artifacts/stories
development_status:
  epic-1: backlog
  1-1-user-authentication: ready-for-dev
  epic-1-retrospective: optional
"""
    doc = SprintStatusParser().parse('/tmp/sprint-status.yaml', text)
    result = SprintStatusValidator().validate(doc, contract)
    assert result.valid is True
