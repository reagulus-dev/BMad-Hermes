from __future__ import annotations

import re
from pathlib import Path

from bmad_workflow_plugin.schemas.artifact_models import ReviewRecordDocument
from .markdown_sections import MarkdownSectionsParser


STORY_KEY_RE = re.compile(r'(?P<epic>\d+)-(?P<story>\d+)-(?P<slug>[a-z0-9-]+)')


class ReviewRecordParser:
    def __init__(self) -> None:
        self.sections_parser = MarkdownSectionsParser()

    def parse(self, path: str, text: str) -> ReviewRecordDocument:
        parsed = self.sections_parser.parse(text)
        fields = parsed.get('fields', {})

        story_key = self._infer_story_key(path, fields)
        review_type = fields.get('Review Type', fields.get('review_type', 'general'))
        status = fields.get('Status', fields.get('status', ''))

        return ReviewRecordDocument(
            path=str(Path(path).resolve()),
            story_key=story_key,
            review_type=review_type,
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
