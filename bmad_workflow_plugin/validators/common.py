from __future__ import annotations

from dataclasses import dataclass

from bmad_workflow_plugin.schemas.common import Message, ValidationResult
from bmad_workflow_plugin.registry.models import ArtifactContract


@dataclass
class ValidationHelpers:
    """Shared validation helpers used by all Phase 1-3 artifact validators."""

    @staticmethod
    def check_status(
        doc: object,
        contract: ArtifactContract,
        errors: list[Message],
    ) -> None:
        doc_status = getattr(doc, 'status', '') or ''
        if not doc_status:
            errors.append(Message(
                code='missing_status',
                message=f'{type(doc).__name__} is missing Status field.',
            ))
            return
        allowed = contract.raw.get('field_definitions', {}).get('status', {}).get('allowed_values', [])
        if allowed and doc_status not in allowed:
            errors.append(Message(
                code='illegal_status_value',
                message=f'Status value "{doc_status}" is not legal.',
                details={'status': doc_status, 'allowed': allowed},
            ))

    @staticmethod
    def check_required_sections(
        doc: object,
        contract: ArtifactContract,
        errors: list[Message],
    ) -> None:
        required = contract.raw.get('section_definitions', {}).get('required', {})
        present = set(getattr(doc, 'sections', {}).keys())
        for section_id in required.keys():
            if section_id not in present:
                errors.append(Message(
                    code='missing_required_section',
                    message=f'Missing required section: {section_id}',
                    details={'section_id': section_id},
                ))

    @staticmethod
    def check_optional_sections(
        doc: object,
        contract: ArtifactContract,
        warnings: list[Message],
    ) -> None:
        optional = contract.raw.get('section_definitions', {}).get('optional', {})
        present = set(getattr(doc, 'sections', {}).keys())
        for section_id in optional.keys():
            if section_id not in present:
                warnings.append(Message(
                    code='missing_optional_section',
                    message=f'Optional section is missing: {section_id}',
                    details={'section_id': section_id},
                ))

    @staticmethod
    def build_result(
        doc: object,
        errors: list[Message],
        warnings: list[Message],
    ) -> ValidationResult:
        doc_class = type(doc).__name__
        return ValidationResult(
            valid=not errors,
            errors=errors,
            warnings=warnings,
            parsed_summary={
                **{f: getattr(doc, f, None) for f in ['path', 'status', 'project_name', 'session_name'] if hasattr(doc, f)},
                'sections_present': sorted(getattr(doc, 'sections', {}).keys()),
            },
        )
