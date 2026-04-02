from __future__ import annotations

from bmad_workflow_plugin.schemas.common import Message, ValidationResult
from bmad_workflow_plugin.schemas.artifact_models import ProductBriefDocument
from bmad_workflow_plugin.registry.models import ArtifactContract
from .common import ValidationHelpers


class ProductBriefValidator:
    def validate(self, doc: ProductBriefDocument, contract: ArtifactContract) -> ValidationResult:
        errors: list[Message] = []
        warnings: list[Message] = []
        ValidationHelpers.check_status(doc, contract, errors)
        ValidationHelpers.check_required_sections(doc, contract, errors)
        ValidationHelpers.check_optional_sections(doc, contract, warnings)
        # Warn if executive_summary is suspiciously short
        summary = doc.sections.get('executive_summary', '')
        if summary and len(summary) < 50:
            warnings.append(Message(
                code='suspiciously_short_section',
                message='Executive Summary appears very short; it should be 2-3 paragraphs.',
                details={'section_id': 'executive_summary', 'length': len(summary)},
            ))
        return ValidationHelpers.build_result(doc, errors, warnings)
