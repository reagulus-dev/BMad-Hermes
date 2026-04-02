from __future__ import annotations

from bmad_workflow_plugin.schemas.common import Message, ValidationResult
from bmad_workflow_plugin.schemas.artifact_models import PRFAQDocument
from bmad_workflow_plugin.registry.models import ArtifactContract
from .common import ValidationHelpers


class PRFAQValidator:
    def validate(self, doc: PRFAQDocument, contract: ArtifactContract) -> ValidationResult:
        errors: list[Message] = []
        warnings: list[Message] = []
        ValidationHelpers.check_status(doc, contract, errors)
        ValidationHelpers.check_required_sections(doc, contract, errors)
        ValidationHelpers.check_optional_sections(doc, contract, warnings)
        # PRFAQ should have a verdict
        if 'verdict' not in doc.sections:
            warnings.append(Message(
                code='missing_optional_section',
                message='PRFAQ is missing The Verdict section.',
                details={'section_id': 'verdict'},
            ))
        return ValidationHelpers.build_result(doc, errors, warnings)
