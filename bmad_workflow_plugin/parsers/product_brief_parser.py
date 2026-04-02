from __future__ import annotations

from pathlib import Path

from bmad_workflow_plugin.schemas.artifact_models import ProductBriefDocument
from .markdown_sections import MarkdownSectionsParser


class ProductBriefParser:
    def __init__(self) -> None:
        self.sections_parser = MarkdownSectionsParser()

    def parse(self, path: str, text: str) -> ProductBriefDocument:
        parsed = self.sections_parser.parse(text)
        fields = parsed.get('fields', {})
        title = parsed.get('title', '') or ''
        # Extract project_name from title like "Product Brief: My Project"
        project_name = self._extract_project_name(title, path)
        status = fields.get('Status', 'draft')
        sections = {k: v['content'] for k, v in parsed.get('sections', {}).items()}
        sections = self._canonicalize_sections(sections)
        return ProductBriefDocument(
            path=str(Path(path).resolve()),
            project_name=project_name,
            status=status,
            sections=sections,
            raw_text=text,
        )

    @staticmethod
    def _extract_project_name(title: str, path: str) -> str:
        import re
        m = re.match(r'Product Brief:\s*(.+)', title)
        if m:
            return m.group(1).strip()
        return Path(path).parent.name

    @staticmethod
    def _canonicalize_sections(sections: dict[str, str]) -> dict[str, str]:
        alias_map = {
            'the_problem': 'problem',
            'the_solution': 'solution',
            'what_makes_this_different': 'differentiators',
        }
        return {alias_map.get(key, key): value for key, value in sections.items()}
