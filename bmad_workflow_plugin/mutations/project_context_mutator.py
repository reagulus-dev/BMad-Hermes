from __future__ import annotations

from bmad_workflow_plugin.schemas.artifact_models import ProjectContextDocument
from .brainstorming_session_mutator import _rebuild_markdown, _get_contract_raw


class ProjectContextMutator:
    """Workflow-aware mutations for ProjectContextDocument.

    Supports replace_section operation for any section.
    Full artifact rewrite allowed by bmad-generate-project-context workflow.
    ProjectContext has no status field.
    """

    def apply_operations(
        self, doc: ProjectContextDocument, workflow_id: str, operations: list[dict], contract
    ) -> ProjectContextDocument:
        sections = dict(doc.sections)

        for op in operations:
            op_type = op.get('type')
            if op_type == 'replace_section':
                sections[op['section_id']] = op.get('new_content', '')
            else:
                raise ValueError(f'Unknown operation type: {op_type!r}')

        new_raw = self._rebuild_raw(doc.project_name, sections, _get_contract_raw(contract))
        return ProjectContextDocument(
            path=doc.path,
            project_name=doc.project_name,
            sections=sections,
            raw_text=new_raw,
        )

    def _rebuild_raw(self, project_name: str, sections: dict[str, str], contract_raw: dict) -> str:
        return _rebuild_markdown(
            f'Project Context for AI Agents: {project_name}',
            {},
            sections,
            contract_raw,
        )
