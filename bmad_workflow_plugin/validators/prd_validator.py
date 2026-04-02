from __future__ import annotations

from bmad_workflow_plugin.schemas.common import Message, ValidationResult
from bmad_workflow_plugin.schemas.artifact_models import PRDDocument
from bmad_workflow_plugin.registry.models import ArtifactContract
from .common import ValidationHelpers


class PRDValidator:
    def validate(self, doc: PRDDocument, contract: ArtifactContract) -> ValidationResult:
        errors: list[Message] = []
        warnings: list[Message] = []
        ValidationHelpers.check_status(doc, contract, errors)
        ValidationHelpers.check_required_sections(doc, contract, errors)
        ValidationHelpers.check_optional_sections(doc, contract, warnings)
        # Check for functional requirements
        fr = doc.sections.get('functional_requirements', '')
        if fr and 'FR-' not in fr and 'Acceptance Criteria' not in fr:
            warnings.append(Message(
                code='suspicious_content',
                message='Functional Requirements section does not contain FR- identifiers or Acceptance Criteria.',
                details={'section_id': 'functional_requirements'},
            ))
        return ValidationHelpers.build_result(doc, errors, warnings)
