from bmad_workflow_plugin.parsers.story_parser import StoryParser


def test_story_parser_extracts_status_and_key() -> None:
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
"""
    doc = StoryParser().parse('/tmp/1-2-user-authentication.md', text)
    assert doc.story_key == '1-2-user-authentication'
    assert doc.status == 'ready-for-dev'
