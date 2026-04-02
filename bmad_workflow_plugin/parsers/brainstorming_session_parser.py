from __future__ import annotations

from pathlib import Path

from bmad_workflow_plugin.schemas.artifact_models import BrainstormingSessionDocument
from .markdown_sections import MarkdownSectionsParser


class BrainstormingSessionParser:
    def __init__(self) -> None:
        self.sections_parser = MarkdownSectionsParser()

    def parse(self, path: str, text: str) -> BrainstormingSessionDocument:
        parsed = self.sections_parser.parse(text)
        fields = parsed.get('fields', {})
        session_name = fields.get('Session', '') or Path(path).stem
        status = fields.get('Status', 'open')
        return BrainstormingSessionDocument(
            path=str(Path(path).resolve()),
            session_name=session_name,
            status=status,
            sections={k: v['content'] for k, v in parsed.get('sections', {}).items()},
            raw_text=text,
        )
