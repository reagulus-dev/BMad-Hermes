from __future__ import annotations

from pathlib import Path

from bmad_workflow_plugin.schemas.artifact_models import ProjectContextDocument
from .markdown_sections import MarkdownSectionsParser


class ProjectContextParser:
    def __init__(self) -> None:
        self.sections_parser = MarkdownSectionsParser()

    def parse(self, path: str, text: str) -> ProjectContextDocument:
        parsed = self.sections_parser.parse(text)
        title = parsed.get('title', '') or ''
        project_name = self._extract_project_name(title, path)
        sections = {k: v['content'] for k, v in parsed.get('sections', {}).items()}
        sections = self._canonicalize_sections(sections)
        return ProjectContextDocument(
            path=str(Path(path).resolve()),
            project_name=project_name,
            sections=sections,
            raw_text=text,
        )

    @staticmethod
    def _extract_project_name(title: str, path: str) -> str:
        import re
        m = re.match(r'Project Context for AI Agents:\s*(.+)', title)
        if m:
            return m.group(1).strip()
        return Path(path).parent.name

    @staticmethod
    def _canonicalize_sections(sections: dict[str, str]) -> dict[str, str]:
        alias_map = {
            'technology_stack_and_versions': 'technology_stack',
            'critical_implementation_rules': 'critical_rules',
            'conventions_and_patterns': 'conventions',
        }
        return {alias_map.get(key, key): value for key, value in sections.items()}
