from __future__ import annotations

from bmad_workflow_plugin.schemas.artifact_models import StoryDocument
from bmad_workflow_plugin.mutations.checkbox_ops import CheckboxOps


class StoryMutator:
    """Workflow-aware section-safe story edits. Never rewrites entire artifact except via create-story."""

    def __init__(self) -> None:
        self._checkbox_ops = CheckboxOps()

    def apply_operations(
        self, doc: StoryDocument, workflow_id: str, operations: list[dict], contract
    ) -> StoryDocument:
        """
        Apply a list of operations to a StoryDocument in-place.

        Supported operation types:
          - checkbox: set a checkbox in tasks_subtasks. Keys: match_text, checked (bool)
          - replace_section: replace an entire section's content. Keys: section_id, new_content

        Permissions:
          - create-story: may rewrite entire artifact
          - all others: only section-level mutations allowed
        """
        # Detect permission
        raw = contract.raw if hasattr(contract, 'raw') else {}
        permissions = raw.get('workflow_permissions', {})
        workflow_perm = permissions.get(workflow_id, {})
        may_rewrite = workflow_perm.get('may_rewrite_entire_artifact', False)

        sections = dict(doc.sections)  # copy

        for op in operations:
            op_type = op.get('type')
            if op_type == 'checkbox':
                if 'tasks_subtasks' not in sections:
                    raise ValueError('tasks_subtasks section not found in story')
                current = sections['tasks_subtasks']
                sections['tasks_subtasks'] = self._checkbox_ops.set_checkbox(
                    current, op['match_text'], bool(op.get('checked'))
                )
            elif op_type == 'replace_section':
                section_id = op.get('section_id')
                if not may_rewrite and section_id not in ('story', 'acceptance_criteria',
                                                          'tasks_subtasks', 'dev_notes',
                                                          'dev_agent_record', 'review_findings',
                                                          'qa_findings', 'evidence_verification'):
                    raise ValueError(f'Section {section_id} is not a valid mutation target')
                sections[section_id] = op.get('new_content', '')
            else:
                raise ValueError(f'Unknown operation type: {op_type!r}')

        # Reconstruct raw_text
        new_raw = self._rebuild_raw(doc.title, doc.status, sections, raw)

        return StoryDocument(
            path=doc.path,
            story_key=doc.story_key,
            title=doc.title,
            status=doc.status,
            sections=sections,
            raw_text=new_raw,
        )

    def _rebuild_raw(self, title: str, status: str, sections: dict[str, str], contract_raw: dict) -> str:
        """Reconstruct full markdown text from title, status, and ordered sections."""
        # Determine canonical section order from contract
        section_defs = contract_raw.get('section_definitions', {})
        required_order = [k for k in section_defs.get('required', {})] if section_defs else []
        optional_order = [k for k in section_defs.get('optional', {})] if section_defs else []

        heading_map = {}
        for sec in list(section_defs.get('required', {}).values()) + list(section_defs.get('optional', {}).values()):
            heading_map[sec.get('section_id', '')] = sec.get('heading', '')

        lines = [f'# {title}', '', f'Status: {status}', '']

        # Emit sections in contract order, then any extra sections not in contract
        emitted = set()
        for key in required_order + optional_order:
            if key in sections:
                heading = heading_map.get(key, key.replace('_', ' ').title())
                lines.append(f'{heading}')
                lines.append('')
                lines.append(sections[key])
                lines.append('')
                emitted.add(key)

        for key, content in sections.items():
            if key not in emitted:
                heading = heading_map.get(key, key.replace('_', ' ').title())
                lines.append(f'## {heading}')
                lines.append('')
                lines.append(content)
                lines.append('')
                emitted.add(key)

        return '\n'.join(lines).strip() + '\n'
