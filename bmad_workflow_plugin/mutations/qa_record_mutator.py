from __future__ import annotations

from bmad_workflow_plugin.schemas.artifact_models import QARecordDocument
from bmad_workflow_plugin.mutations.checkbox_ops import CheckboxOps


class QARecordMutator:
    """
    Section-safe QA record edits.
    Supports: checkbox, replace_section, set_status operations.
    """

    def __init__(self) -> None:
        self._checkbox_ops = CheckboxOps()

    def apply_operations(
        self, doc: QARecordDocument, workflow_id: str, operations: list[dict], contract
    ) -> QARecordDocument:
        raw = contract.raw if hasattr(contract, 'raw') else {}
        permissions = raw.get('workflow_permissions', {})
        workflow_perm = permissions.get(workflow_id, {})
        may_rewrite = workflow_perm.get('may_rewrite_entire_artifact', False)

        sections = dict(doc.sections)

        for op in operations:
            op_type = op.get('type')
            if op_type == 'checkbox':
                if 'test_results' not in sections:
                    raise ValueError('test_results section not found in QA record')
                sections['test_results'] = self._checkbox_ops.set_checkbox(
                    sections['test_results'], op['match_text'], bool(op.get('checked'))
                )
            elif op_type == 'replace_section':
                section_id = op.get('section_id')
                allowed = self._allowed_sections(contract) if may_rewrite else self._mutation_target_sections()
                if section_id not in allowed:
                    raise ValueError(f'Section {section_id} is not a valid mutation target for qa_record')
                sections[section_id] = op.get('new_content', '')
            elif op_type == 'set_status':
                new_status = op.get('status', '')
                new_raw = self._rebuild_raw(doc.story_key, doc.qa_type, new_status, sections, raw)
                return QARecordDocument(
                    path=doc.path,
                    story_key=doc.story_key,
                    qa_type=doc.qa_type,
                    status=new_status,
                    sections=sections,
                    raw_text=new_raw,
                )
            else:
                raise ValueError(f'Unknown operation type: {op_type!r}')

        new_raw = self._rebuild_raw(doc.story_key, doc.qa_type, doc.status, sections, raw)
        return QARecordDocument(
            path=doc.path,
            story_key=doc.story_key,
            qa_type=doc.qa_type,
            status=doc.status,
            sections=sections,
            raw_text=new_raw,
        )

    def _allowed_sections(self, contract) -> set[str]:
        raw = contract.raw if hasattr(contract, 'raw') else {}
        required = set(raw.get('section_definitions', {}).get('required', {}).keys())
        optional = set(raw.get('section_definitions', {}).get('optional', {}).keys())
        return required | optional

    def _mutation_target_sections(self) -> set[str]:
        return {'qa_summary', 'test_results', 'issues_found', 'notes', 'qa_agent_record'}

    def _rebuild_raw(
        self, story_key: str, qa_type: str, status: str, sections: dict[str, str], contract_raw: dict
    ) -> str:
        section_defs = contract_raw.get('section_definitions', {})
        required_order = list(section_defs.get('required', {}).keys())
        optional_order = list(section_defs.get('optional', {}).keys())

        heading_map = {}
        for sec in list(section_defs.get('required', {}).values()) + list(section_defs.get('optional', {}).values()):
            heading_map[sec.get('section_id', '')] = sec.get('heading', '')

        lines = [
            f'QA Record: {story_key}',
            '',
            f'QA Type: {qa_type}',
            f'Status: {status}',
            '',
        ]

        emitted = set()
        for key in required_order + optional_order:
            if key in sections:
                heading = heading_map.get(key, key.replace('_', ' ').title())
                lines.extend([heading, '', sections[key], ''])
                emitted.add(key)

        for key, content in sections.items():
            if key not in emitted:
                heading = heading_map.get(key, key.replace('_', ' ').title())
                lines.extend([f'## {heading}', '', content, ''])

        return '\n'.join(lines).strip() + '\n'
