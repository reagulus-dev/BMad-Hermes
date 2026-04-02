from __future__ import annotations

from bmad_workflow_plugin.schemas.artifact_models import PRDValidationReportDocument
from .brainstorming_session_mutator import _rebuild_markdown, _get_contract_raw


class PRDValidationReportMutator:
    """Workflow-aware mutations for PRDValidationReportDocument.

    Supports replace_section operation for any section.
    Full artifact rewrite allowed by bmad-validate-prd workflow.
    """

    def apply_operations(
        self, doc: PRDValidationReportDocument, workflow_id: str, operations: list[dict], contract
    ) -> PRDValidationReportDocument:
        sections = dict(doc.sections)

        for op in operations:
            op_type = op.get('type')
            if op_type == 'replace_section':
                sections[op['section_id']] = op.get('new_content', '')
            else:
                raise ValueError(f'Unknown operation type: {op_type!r}')

        new_raw = self._rebuild_raw(doc.project_name, doc.status, doc.validation_type, sections, _get_contract_raw(contract))
        return PRDValidationReportDocument(
            path=doc.path,
            project_name=doc.project_name,
            status=doc.status,
            validation_type=doc.validation_type,
            sections=sections,
            raw_text=new_raw,
        )

    def _rebuild_raw(self, project_name: str, status: str, validation_type: str, sections: dict[str, str], contract_raw: dict) -> str:
        return _rebuild_markdown(
            f'PRD Validation Report: {project_name}',
            {'Status': status, 'Validation Type': validation_type},
            sections,
            contract_raw,
        )
