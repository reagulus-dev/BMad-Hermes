from __future__ import annotations

from bmad_workflow_plugin.schemas.common import Message, ValidationResult
from bmad_workflow_plugin.schemas.artifact_models import UXDesignDocument
from bmad_workflow_plugin.registry.models import ArtifactContract
from .common import ValidationHelpers


class UXDesignValidator:
    def validate(self, doc: UXDesignDocument, contract: ArtifactContract) -> ValidationResult:
        errors: list[Message] = []
        warnings: list[Message] = []
        ValidationHelpers.check_status(doc, contract, errors)
        ValidationHelpers.check_required_sections(doc, contract, errors)
        ValidationHelpers.check_optional_sections(doc, contract, warnings)
        return ValidationHelpers.build_result(doc, errors, warnings)
