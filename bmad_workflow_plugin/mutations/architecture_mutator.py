from __future__ import annotations

from bmad_workflow_plugin.schemas.artifact_models import ArchitectureDocument
from .brainstorming_session_mutator import _rebuild_markdown, _get_contract_raw


class ArchitectureMutator:
    """Workflow-aware mutations for ArchitectureDocument.

    Supports replace_section operation for any section.
    Full artifact rewrite allowed by bmad-create-architecture workflow.
    """

    def apply_operations(
        self, doc: ArchitectureDocument, workflow_id: str, operations: list[dict], contract
    ) -> ArchitectureDocument:
        sections = dict(doc.sections)

        for op in operations:
            op_type = op.get('type')
            if op_type == 'replace_section':
                sections[op['section_id']] = op.get('new_content', '')
            else:
                raise ValueError(f'Unknown operation type: {op_type!r}')

        new_raw = self._rebuild_raw(doc.project_name, doc.status, sections, _get_contract_raw(contract))
        return ArchitectureDocument(
            path=doc.path,
            project_name=doc.project_name,
            status=doc.status,
            sections=sections,
            raw_text=new_raw,
        )

    def _rebuild_raw(self, project_name: str, status: str, sections: dict[str, str], contract_raw: dict) -> str:
        return _rebuild_markdown(
            f'Architecture Decision Document: {project_name}',
            {'Status': status},
            sections,
            contract_raw,
        )
