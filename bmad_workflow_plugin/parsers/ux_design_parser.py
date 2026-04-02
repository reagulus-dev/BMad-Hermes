from __future__ import annotations

from pathlib import Path

from bmad_workflow_plugin.schemas.artifact_models import UXDesignDocument
from .markdown_sections import MarkdownSectionsParser


class UXDesignParser:
    def __init__(self) -> None:
        self.sections_parser = MarkdownSectionsParser()

    def parse(self, path: str, text: str) -> UXDesignDocument:
        parsed = self.sections_parser.parse(text)
        fields = parsed.get('fields', {})
        title = parsed.get('title', '') or ''
        project_name = self._extract_project_name(title, path)
        status = fields.get('Status', 'draft')
        return UXDesignDocument(
            path=str(Path(path).resolve()),
            project_name=project_name,
            status=status,
            sections={k: v['content'] for k, v in parsed.get('sections', {}).items()},
            raw_text=text,
        )

    @staticmethod
    def _extract_project_name(title: str, path: str) -> str:
        import re
        m = re.match(r'UX Design:\s*(.+)', title)
        if m:
            return m.group(1).strip()
        return Path(path).parent.name
