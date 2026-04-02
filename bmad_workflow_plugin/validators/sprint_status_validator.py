from __future__ import annotations

import re

from bmad_workflow_plugin.schemas.common import ValidationResult, Message
from bmad_workflow_plugin.schemas.artifact_models import SprintStatusDocument
from bmad_workflow_plugin.registry.models import ArtifactContract


EPIC_RE = re.compile(r'^epic-\d+$')
RETRO_RE = re.compile(r'^epic-\d+-retrospective$')
STORY_RE = re.compile(r'^\d+-\d+-[a-z0-9-]+$')


class SprintStatusValidator:
    def validate(self, doc: SprintStatusDocument, contract: ArtifactContract, previous_doc: SprintStatusDocument | None = None) -> ValidationResult:
        errors: list[Message] = []
        warnings: list[Message] = []
        raw = contract.raw

        required_top = raw.get('top_level_keys', {}).get('required', [])
        for key in required_top:
            if doc.metadata.get(key) is None and key != 'development_status':
                errors.append(Message(code='missing_required_key', message=f'Missing required top-level key: {key}', details={'key': key}))

        if not isinstance(doc.development_status, list):
            errors.append(Message(code='invalid_development_status', message='development_status must parse as an ordered list of entries.'))

        statuses = raw.get('status_model', {})
        previous_map = {e.key: e.status for e in previous_doc.development_status} if previous_doc else {}

        last_epic_num = None
        seen_keys: set[str] = set()
        for entry in doc.development_status:
            if entry.key in seen_keys:
                errors.append(Message(code='duplicate_key', message='Duplicate development_status key.', details={'key': entry.key}))
            seen_keys.add(entry.key)

            if entry.entry_type == 'epic':
                if not EPIC_RE.match(entry.key):
                    errors.append(Message(code='invalid_epic_key', message='Invalid epic key pattern.', details={'key': entry.key}))
                legal = statuses.get('epic', {}).get('legal_values', [])
                epic_num = int(entry.key.split('-')[1]) if entry.key.split('-')[1].isdigit() else None
                last_epic_num = epic_num
            elif entry.entry_type == 'retrospective':
                if not RETRO_RE.match(entry.key):
                    errors.append(Message(code='invalid_retrospective_key', message='Invalid retrospective key pattern.', details={'key': entry.key}))
                legal = statuses.get('retrospective', {}).get('legal_values', [])
                # ordering check: retro should follow some epic
                if last_epic_num is None:
                    errors.append(Message(code='invalid_ordering', message='Retrospective appears before any epic.', details={'key': entry.key}))
            else:
                if not STORY_RE.match(entry.key):
                    errors.append(Message(code='invalid_story_key', message='Invalid story key pattern.', details={'key': entry.key}))
                legal = statuses.get('story', {}).get('legal_values', [])
                try:
                    epic_num = int(entry.key.split('-')[0])
                except ValueError:
                    epic_num = None
                if last_epic_num is not None and epic_num is not None and epic_num < last_epic_num:
                    errors.append(Message(code='invalid_ordering', message='Story ordering violates epic grouping.', details={'key': entry.key}))

            if legal and entry.status not in legal:
                errors.append(Message(code='illegal_status_value', message='Illegal sprint status value.', details={'key': entry.key, 'status': entry.status, 'entry_type': entry.entry_type}))

            previous_status = previous_map.get(entry.key)
            if previous_status and previous_status != entry.status:
                transitions = statuses.get(entry.entry_type, {}).get('transitions', {})
                allowed = transitions.get(previous_status, {}).get('allowed_next', [])
                if entry.status not in allowed:
                    errors.append(Message(code='illegal_status_transition', message='Illegal sprint status transition.', details={'key': entry.key, 'from': previous_status, 'to': entry.status}))

        raw_text = doc.raw_text or ''
        if 'STATUS DEFINITIONS' not in raw_text:
            warnings.append(Message(code='missing_comment_block', message='Preferred comment block STATUS DEFINITIONS is missing.'))
        if 'WORKFLOW NOTES' not in raw_text:
            warnings.append(Message(code='missing_comment_block', message='Preferred comment block WORKFLOW NOTES is missing.'))

        return ValidationResult(
            valid=not errors,
            errors=errors,
            warnings=warnings,
            parsed_summary={
                'metadata': doc.metadata,
                'entry_count': len(doc.development_status),
                'keys': [e.key for e in doc.development_status],
            },
        )
