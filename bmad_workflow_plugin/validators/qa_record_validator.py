from __future__ import annotations

from bmad_workflow_plugin.schemas.common import Message, ValidationResult
from bmad_workflow_plugin.schemas.artifact_models import QARecordDocument
from bmad_workflow_plugin.registry.models import ArtifactContract


class QARecordValidator:
    def validate(
        self, doc: QARecordDocument, contract: ArtifactContract,
        previous_doc: QARecordDocument | None = None
    ) -> ValidationResult:
        errors: list[Message] = []
        warnings: list[Message] = []
        raw = contract.raw

        # Validate qa_type
        qa_types = raw.get('field_definitions', {}).get('qa_type', {}).get('allowed_values', [])
        if qa_types and doc.qa_type not in qa_types:
            errors.append(Message(
                code='illegal_qa_type',
                message='qa_type is not a legal value.',
                details={'qa_type': doc.qa_type},
            ))

        # Validate status
        status_values = raw.get('field_definitions', {}).get('status', {}).get('allowed_values', [])
        if not doc.status:
            errors.append(Message(code='missing_status', message='QA record is missing Status field.'))
        elif status_values and doc.status not in status_values:
            errors.append(Message(
                code='illegal_status_value',
                message='Status is not a legal value.',
                details={'status': doc.status},
            ))

        # Validate story_key
        if not doc.story_key:
            errors.append(Message(code='missing_story_key', message='QA record is missing story_key.'))

        # Required sections
        required = raw.get('section_definitions', {}).get('required', {})
        section_keys = set(doc.sections.keys())
        for section_id in required.keys():
            if section_id not in section_keys:
                errors.append(Message(
                    code='missing_required_section',
                    message=f'Missing required section: {section_id}',
                    details={'section_id': section_id},
                ))

        # Optional section warnings
        optional = raw.get('section_definitions', {}).get('optional', {})
        for section_id in optional.keys():
            if section_id not in section_keys:
                warnings.append(Message(
                    code='missing_optional_section',
                    message=f'Optional section is missing: {section_id}',
                    details={'section_id': section_id},
                ))

        return ValidationResult(
            valid=not errors,
            errors=errors,
            warnings=warnings,
            parsed_summary={
                'story_key': doc.story_key,
                'qa_type': doc.qa_type,
                'status': doc.status,
                'sections_present': sorted(doc.sections.keys()),
            },
        )
