from __future__ import annotations

from bmad_workflow_plugin.schemas.common import Message, ValidationResult
from bmad_workflow_plugin.schemas.artifact_models import EpicsAndStoriesDocument
from bmad_workflow_plugin.registry.models import ArtifactContract
from .common import ValidationHelpers


class EpicsAndStoriesValidator:
    def validate(self, doc: EpicsAndStoriesDocument, contract: ArtifactContract) -> ValidationResult:
        errors: list[Message] = []
        warnings: list[Message] = []
        ValidationHelpers.check_status(doc, contract, errors)
        ValidationHelpers.check_required_sections(doc, contract, errors)
        ValidationHelpers.check_optional_sections(doc, contract, warnings)
        # Epic list should have some epic markers
        epic_section = doc.sections.get('epic_list', '')
        if epic_section and 'Epic' not in epic_section and 'epic' not in epic_section.lower():
            warnings.append(Message(
                code='suspicious_content',
                message='Epic List section does not contain "Epic" references.',
                details={'section_id': 'epic_list'},
            ))
        return ValidationHelpers.build_result(doc, errors, warnings)
