from __future__ import annotations

from bmad_workflow_plugin.schemas.common import Message, ValidationResult
from bmad_workflow_plugin.schemas.artifact_models import ProjectContextDocument
from bmad_workflow_plugin.registry.models import ArtifactContract
from .common import ValidationHelpers


class ProjectContextValidator:
    def validate(self, doc: ProjectContextDocument, contract: ArtifactContract) -> ValidationResult:
        errors: list[Message] = []
        warnings: list[Message] = []
        # Project context has no status field
        ValidationHelpers.check_required_sections(doc, contract, errors)
        ValidationHelpers.check_optional_sections(doc, contract, warnings)
        # critical_rules is especially important
        if 'critical_rules' not in doc.sections:
            warnings.append(Message(
                code='missing_optional_section',
                message='Project Context is missing Critical Implementation Rules section.',
                details={'section_id': 'critical_rules'},
            ))
        return ValidationHelpers.build_result(doc, errors, warnings)
