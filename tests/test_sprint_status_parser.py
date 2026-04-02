from bmad_workflow_plugin.parsers.sprint_status_parser import SprintStatusParser


def test_sprint_status_parser_parses_entries() -> None:
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
    assert doc.metadata['project'] == 'demo'
    assert len(doc.development_status) == 3
    assert doc.development_status[1].entry_type == 'story'


def test_sprint_status_parser_parses_real_export_nested_sprints_yaml() -> None:
    text = """metadata:
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
    doc = SprintStatusParser().parse('/tmp/sprint-status.yaml', text)

    assert doc.metadata['project'] == 'LapseLess'
    assert [entry.key for entry in doc.development_status] == ['1-1', '1-7']
    assert [entry.status for entry in doc.development_status] == ['done', 'backlog']


def test_sprint_status_parser_parses_real_export_markdown_status_tables() -> None:
    text = """# Sprint Status — ProofKey

**Project:** ProofKey
**Generated:** 2026-03-18 21:53 UTC
**Tracking System:** file-system
**Story Location:** `/tmp/stories`

## Development Status

### Epic 1: Property Onboarding & Session Setup
| Story | Status |
|-------|--------|
| 1-1-create-property-record | complete |
| 1-2-country-deposit-framework | pending |
| **Epic 1 Retrospective** | pending |
| **Epic 1 QA Report** | generated |
"""
    doc = SprintStatusParser().parse('/tmp/sprint-status.yaml', text)

    assert doc.metadata['project'] == 'ProofKey'
    assert [entry.key for entry in doc.development_status] == [
        '1-1-create-property-record',
        '1-2-country-deposit-framework',
        'epic-1-retrospective',
    ]
    assert [entry.status for entry in doc.development_status] == ['done', 'backlog', 'backlog']
