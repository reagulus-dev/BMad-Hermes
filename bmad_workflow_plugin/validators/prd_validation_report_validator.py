from __future__ import annotations

from bmad_workflow_plugin.schemas.common import Message, ValidationResult
from bmad_workflow_plugin.schemas.artifact_models import PRDValidationReportDocument
from bmad_workflow_plugin.registry.models import ArtifactContract
from .common import ValidationHelpers


class PRDValidationReportValidator:
    def validate(self, doc: PRDValidationReportDocument, contract: ArtifactContract) -> ValidationResult:
        errors: list[Message] = []
        warnings: list[Message] = []
        ValidationHelpers.check_status(doc, contract, errors)
        ValidationHelpers.check_required_sections(doc, contract, errors)
        ValidationHelpers.check_optional_sections(doc, contract, warnings)
        # Validation type must be in allowed list
        allowed = contract.raw.get('field_definitions', {}).get('validation_type', {}).get('allowed_values', [])
        if allowed and doc.validation_type not in allowed:
            errors.append(Message(
                code='illegal_validation_type',
                message=f'validation_type "{doc.validation_type}" is not in allowed values.',
                details={'validation_type': doc.validation_type, 'allowed': allowed},
            ))
        return ValidationHelpers.build_result(doc, errors, warnings)
