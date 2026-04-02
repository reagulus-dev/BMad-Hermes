from __future__ import annotations

from bmad_workflow_plugin.schemas.common import Message, ValidationResult
from bmad_workflow_plugin.schemas.artifact_models import ArchitectureDocument
from bmad_workflow_plugin.registry.models import ArtifactContract
from .common import ValidationHelpers


class ArchitectureValidator:
    def validate(self, doc: ArchitectureDocument, contract: ArtifactContract) -> ValidationResult:
        errors: list[Message] = []
        warnings: list[Message] = []
        ValidationHelpers.check_status(doc, contract, errors)
        ValidationHelpers.check_required_sections(doc, contract, errors)
        ValidationHelpers.check_optional_sections(doc, contract, warnings)
        # Architecture should have at least one AD-## decision
        ad_section = doc.sections.get('architectural_decisions', '')
        if ad_section and 'AD-' not in ad_section:
            warnings.append(Message(
                code='suspicious_content',
                message='Architectural Decisions section does not contain AD- identifiers.',
                details={'section_id': 'architectural_decisions'},
            ))
        return ValidationHelpers.build_result(doc, errors, warnings)
