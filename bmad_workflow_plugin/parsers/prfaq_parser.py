from __future__ import annotations

from pathlib import Path
import re

from bmad_workflow_plugin.schemas.artifact_models import PRFAQDocument
from .markdown_sections import MarkdownSectionsParser


class PRFAQParser:
    def __init__(self) -> None:
        self.sections_parser = MarkdownSectionsParser()

    def parse(self, path: str, text: str) -> PRFAQDocument:
        parsed = self.sections_parser.parse(text)
        fields = parsed.get('fields', {})
        title = parsed.get('title', '') or ''
        project_name = self._extract_project_name(title, path)
        status = fields.get('Status', 'draft')
        sections = {k: v['content'] for k, v in parsed.get('sections', {}).items()}
        sections = self._canonicalize_sections(title, text, sections)
        return PRFAQDocument(
            path=str(Path(path).resolve()),
            project_name=project_name,
            status=status,
            sections=sections,
            raw_text=text,
        )

    @staticmethod
    def _extract_project_name(title: str, path: str) -> str:
        m = re.match(r'PRFAQ:\s*(.+)', title)
        if m:
            return m.group(1).strip()
        return Path(path).parent.name

    @staticmethod
    def _canonicalize_sections(title: str, text: str, sections: dict[str, str]) -> dict[str, str]:
        canonical = dict(sections)

        headline = PRFAQParser._extract_first_h1_after_title(text)
        if headline:
            canonical['headline'] = headline

        press_release = PRFAQParser._extract_press_release_body(text)
        if press_release:
            canonical['press_release'] = press_release

        if 'the_verdict' in canonical and 'verdict' not in canonical:
            canonical['verdict'] = canonical.pop('the_verdict')

        return canonical

    @staticmethod
    def _extract_first_h1_after_title(text: str) -> str:
        matches = re.findall(r'^#\s+(.+)$', text, flags=re.MULTILINE)
        if len(matches) >= 2:
            return matches[1].strip()
        return ''

    @staticmethod
    def _extract_press_release_body(text: str) -> str:
        lines = text.splitlines()
        h1_seen = 0
        capture = False
        collected: list[str] = []

        for line in lines:
            if line.startswith('# '):
                h1_seen += 1
                if h1_seen == 2:
                    capture = True
                    continue
            if capture and line.startswith('### '):
                break
            if capture:
                collected.append(line)

        return '\n'.join(collected).strip()
