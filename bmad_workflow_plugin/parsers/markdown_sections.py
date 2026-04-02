from __future__ import annotations

import re
from typing import Any


FIELD_RE = re.compile(r'^(?P<label>[A-Za-z][A-Za-z0-9 _\-/]+):\s*(?P<value>.*)$')
HEADING_RE = re.compile(r'^(?P<level>#{1,6})\s+(?P<title>.+?)\s*$')


class MarkdownSectionsParser:
    def parse(self, text: str) -> dict[str, Any]:
        lines = text.splitlines()
        title = None
        fields: dict[str, str] = {}
        sections: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None

        for line in lines:
            heading_match = HEADING_RE.match(line)
            if heading_match:
                if current is not None:
                    current['content'] = '\n'.join(current['content_lines']).rstrip()
                    sections.append(current)
                level = len(heading_match.group('level'))
                heading = heading_match.group('title').strip()
                if level == 1 and title is None:
                    title = heading
                    current = None
                    continue
                current = {
                    'level': level,
                    'heading': heading,
                    'content_lines': [],
                }
                continue

            if current is None:
                field_match = FIELD_RE.match(line.strip())
                if field_match:
                    fields[field_match.group('label').strip()] = field_match.group('value').strip()
                continue

            current['content_lines'].append(line)

        if current is not None:
            current['content'] = '\n'.join(current['content_lines']).rstrip()
            sections.append(current)

        normalized_sections: dict[str, dict[str, Any]] = {}
        seen: dict[str, int] = {}
        for section in sections:
            base_key = self._normalize_heading(section['heading'])
            count = seen.get(base_key, 0)
            seen[base_key] = count + 1
            key = base_key if count == 0 else f'{base_key}__{count + 1}'
            normalized_sections[key] = {
                'heading': section['heading'],
                'level': section['level'],
                'content': section['content'],
            }

        return {
            'title': title,
            'fields': fields,
            'sections': normalized_sections,
            'raw_text': text,
        }

    @staticmethod
    def _normalize_heading(heading: str) -> str:
        key = heading.strip().lower()
        key = key.replace('&', 'and')
        key = re.sub(r'[^a-z0-9]+', '_', key)
        key = re.sub(r'_+', '_', key).strip('_')
        return key
