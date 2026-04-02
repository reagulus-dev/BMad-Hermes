from __future__ import annotations

import re

from bmad_workflow_plugin.schemas.common import Message, ValidationResult
from bmad_workflow_plugin.schemas.artifact_models import StoryDocument
from bmad_workflow_plugin.registry.models import ArtifactContract


CHECKBOX_RE = re.compile(r'^\s*-\s*\[(?: |x|X)\]\s+')
TITLE_RE = re.compile(r'^Story\s+\d+\.\d+:\s+.+$')


class StoryValidator:
    def validate(self, doc: StoryDocument, contract: ArtifactContract, previous_status: str | None = None) -> ValidationResult:
        errors: list[Message] = []
        warnings: list[Message] = []
        raw = contract.raw

        if not doc.title:
            errors.append(Message(code='missing_title', message='Story is missing an H1 title.'))
        elif not TITLE_RE.match(doc.title):
            errors.append(Message(code='invalid_title', message='Story title does not match expected pattern.', details={'title': doc.title}))

        status_values = raw.get('field_definitions', {}).get('status', {}).get('allowed_values', [])
        if not doc.status:
            errors.append(Message(code='missing_status', message='Story is missing Status field.'))
        elif status_values and doc.status not in status_values:
            errors.append(Message(code='illegal_status_value', message='Story status is not legal.', details={'status': doc.status}))

        required_sections = raw.get('section_definitions', {}).get('required', {})
        section_keys = set(doc.sections.keys())
        for section_id in required_sections.keys():
            if section_id not in section_keys:
                errors.append(Message(code='missing_required_section', message=f'Missing required section: {section_id}', details={'section_id': section_id}))

        tasks = doc.sections.get('tasks_subtasks', '')
        if tasks:
            if not any(CHECKBOX_RE.match(line) for line in tasks.splitlines() if line.strip()):
                errors.append(Message(code='invalid_tasks_format', message='Tasks / Subtasks section does not contain checkbox lines.'))

        if previous_status and doc.status and previous_status != doc.status:
            transitions = raw.get('transitions', {}).get('status', {})
            allowed = transitions.get(previous_status, {}).get('allowed_next', [])
            if doc.status not in allowed:
                errors.append(Message(
                    code='illegal_status_transition',
                    message='Illegal story status transition.',
                    details={'from': previous_status, 'to': doc.status},
                ))

        if 'review_findings' not in doc.sections:
            warnings.append(Message(code='missing_optional_section', message='Optional section review_findings is missing.'))
        if 'qa_findings' not in doc.sections:
            warnings.append(Message(code='missing_optional_section', message='Optional section qa_findings is missing.'))
        if 'evidence_verification' not in doc.sections:
            warnings.append(Message(code='missing_optional_section', message='Optional section evidence_verification is missing.'))

        return ValidationResult(
            valid=not errors,
            errors=errors,
            warnings=warnings,
            parsed_summary={
                'title': doc.title,
                'status': doc.status,
                'sections_present': sorted(doc.sections.keys()),
            },
        )
