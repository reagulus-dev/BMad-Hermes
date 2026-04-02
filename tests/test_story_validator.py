from bmad_workflow_plugin.registry.loader import RegistryLoader
from bmad_workflow_plugin.parsers.story_parser import StoryParser
from bmad_workflow_plugin.validators.story_validator import StoryValidator


def test_story_validator_accepts_basic_valid_story() -> None:
    registry = RegistryLoader().load_default()
    contract = registry['story']
    text = """# Story 1.2: User Authentication

Status: ready-for-dev

## Story

As a user...

## Acceptance Criteria

1. Works

## Tasks / Subtasks

- [ ] Task 1

## Dev Notes

notes

## Dev Agent Record

### Agent Model Used

gpt

### Debug Log References

### Completion Notes List

### File List

## Review Findings

<!-- Append code review findings here. -->

## QA Findings

<!-- Append QA results here. -->

## Evidence / Verification

<!-- Runtime verification notes. -->
"""
    doc = StoryParser().parse('/tmp/1-2-user-authentication.md', text)
    result = StoryValidator().validate(doc, contract)
    assert result.valid is True
