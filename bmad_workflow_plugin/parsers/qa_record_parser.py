from __future__ import annotations

import re
from pathlib import Path

from bmad_workflow_plugin.schemas.artifact_models import QARecordDocument
from .markdown_sections import MarkdownSectionsParser


STORY_KEY_RE = re.compile(r'(?P<epic>\d+)-(?P<story>\d+)-(?P<slug>[a-z0-9-]+)')


class QARecordParser:
    def __init__(self) -> None:
        self.sections_parser = MarkdownSectionsParser()

    def parse(self, path: str, text: str) -> QARecordDocument:
        parsed = self.sections_parser.parse(text)
        fields = parsed.get('fields', {})

        story_key = self._infer_story_key(path, fields)
        qa_type = fields.get('QA Type', fields.get('qa_type', 'functional'))
        status = fields.get('Status', fields.get('status', ''))

        return QARecordDocument(
            path=str(Path(path).resolve()),
            story_key=story_key,
            qa_type=qa_type,
            status=status,
            sections={k: v['content'] for k, v in parsed.get('sections', {}).items()},
            raw_text=text,
        )

    def _infer_story_key(self, path: str, fields: dict) -> str:
        # Try from path
        match = STORY_KEY_RE.search(path)
        if match:
            return match.group(0)
        # Fall back to Story Key field
        return fields.get('Story Key', fields.get('story_key', Path(path).stem))
