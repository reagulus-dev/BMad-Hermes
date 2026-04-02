from __future__ import annotations

import re
from pathlib import Path

from bmad_workflow_plugin.schemas.artifact_models import StoryDocument
from .markdown_sections import MarkdownSectionsParser


TITLE_RE = re.compile(r'^Story\s+(?P<epic>\d+)\.(?P<story>\d+):\s+(?P<title>.+)$')
STORY_KEY_FROM_NAME_RE = re.compile(r'(?P<epic>\d+)-(?P<story>\d+)-(?P<slug>[a-z0-9-]+)')


class StoryParser:
    def __init__(self) -> None:
        self.sections_parser = MarkdownSectionsParser()

    def parse(self, path: str, text: str) -> StoryDocument:
        parsed = self.sections_parser.parse(text)
        title = parsed.get('title') or ''
        status = parsed.get('fields', {}).get('Status', '')

        epic_num = ''
        story_num = ''
        story_title = title
        title_match = TITLE_RE.match(title)
        if title_match:
            epic_num = title_match.group('epic')
            story_num = title_match.group('story')
            story_title = title_match.group('title').strip()

        story_key = self._infer_story_key(path, epic_num, story_num, story_title)
        return StoryDocument(
            path=str(Path(path).resolve()),
            story_key=story_key,
            title=title,
            status=status,
            sections={k: v['content'] for k, v in parsed.get('sections', {}).items()},
            raw_text=text,
        )

    def _infer_story_key(self, path: str, epic_num: str, story_num: str, story_title: str) -> str:
        filename = Path(path).stem
        match = STORY_KEY_FROM_NAME_RE.search(filename)
        if match:
            return match.group(0)
        if epic_num and story_num and story_title:
            slug = re.sub(r'[^a-z0-9]+', '-', story_title.lower()).strip('-')
            return f'{epic_num}-{story_num}-{slug}'
        return filename
