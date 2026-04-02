from __future__ import annotations

from bmad_workflow_plugin.schemas.artifact_models import BrainstormingSessionDocument


class BrainstormingSessionMutator:
    """Workflow-aware mutations for BrainstormingSessionDocument.

    Supports replace_section operation for any section.
    Full artifact rewrite allowed by bmad-brainstorming workflow.
    """

    def apply_operations(
        self, doc: BrainstormingSessionDocument, workflow_id: str, operations: list[dict], contract
    ) -> BrainstormingSessionDocument:
        sections = dict(doc.sections)

        for op in operations:
            op_type = op.get('type')
            if op_type == 'replace_section':
                sections[op['section_id']] = op.get('new_content', '')
            else:
                raise ValueError(f'Unknown operation type: {op_type!r}')

        new_raw = self._rebuild_raw(doc.session_name, doc.status, sections, _get_contract_raw(contract))
        return BrainstormingSessionDocument(
            path=doc.path,
            session_name=doc.session_name,
            status=doc.status,
            sections=sections,
            raw_text=new_raw,
        )

    def _rebuild_raw(self, session_name: str, status: str, sections: dict[str, str], contract_raw: dict) -> str:
        return _rebuild_markdown(
            f'Brainstorming Session: {session_name}',
            {'Status': status},
            sections,
            contract_raw,
        )


def _get_contract_raw(contract) -> dict:
    return contract.raw if hasattr(contract, 'raw') else {}


def _rebuild_markdown(title: str, fields: dict[str, str], sections: dict[str, str], contract_raw: dict) -> str:
    section_defs = contract_raw.get('section_definitions', {})
    heading_map = {
        **{s['section_id']: s['heading'] for s in section_defs.get('required', {}).values()},
        **{s['section_id']: s['heading'] for s in section_defs.get('optional', {}).values()},
    }
    required_order = list(section_defs.get('required', {}).keys())
    optional_order = list(section_defs.get('optional', {}).keys())

    lines = [f'# {title}', '']
    for label, value in fields.items():
        if value:
            lines.append(f'**{label}:** {value}')
    lines.append('')

    emitted = set()
    for key in required_order + optional_order:
        if key in sections:
            heading = heading_map.get(key, key.replace('_', ' ').title())
            lines.append(f'## {heading}')
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

    return '\n'.join(lines).strip() + '\n'
