from __future__ import annotations

from pathlib import Path
import re
import yaml

from bmad_workflow_plugin.schemas.artifact_models import SprintStatusDocument, SprintStatusEntry


_BOLD_METADATA_RE = re.compile(r'^\*\*(?P<key>[^*]+):\*\*\s*(?P<value>.+?)\s*$')
_EPIC_HEADING_RE = re.compile(r'^###\s+Epic\s+(?P<epic>\d+)\b')
_TABLE_ROW_RE = re.compile(r'^\|\s*(?P<left>.+?)\s*\|\s*(?P<right>.+?)\s*\|\s*$')
_STORY_ID_DOTTED_RE = re.compile(r'^(?P<epic>\d+)\.(?P<story>\d+)$')
_STORY_ID_SHORT_RE = re.compile(r'^(?P<epic>\d+)-(?P<story>\d+)$')
_INVALID_NESTED_KEY_RE = re.compile(r'^(?P<indent>\s+)(?P<key>[A-Za-z0-9_-]+):\s+(?P<value>[^#\n]+?)\s*$')


class SprintStatusParser:
    def parse(self, path: str, text: str) -> SprintStatusDocument:
        metadata, entries = self._parse_markdown_table_status(text)
        if entries:
            return SprintStatusDocument(
                path=str(Path(path).resolve()),
                metadata=metadata,
                development_status=entries,
                raw_text=text,
            )

        payload = self._load_structured_payload(text)
        metadata = self._extract_metadata(payload)
        entries = self._extract_entries(payload)
        if not entries:
            entries = self._extract_line_oriented_entries(text)
        return SprintStatusDocument(
            path=str(Path(path).resolve()),
            metadata=metadata,
            development_status=entries,
            raw_text=text,
        )

    def _parse_markdown_table_status(self, text: str) -> tuple[dict, list[SprintStatusEntry]]:
        metadata: dict[str, str] = {}
        entries: list[SprintStatusEntry] = []
        current_epic: str | None = None
        in_dev_section = False

        for line in text.splitlines():
            stripped = line.strip()
            meta_match = _BOLD_METADATA_RE.match(stripped)
            if meta_match:
                key = meta_match.group('key').strip().lower().replace(' ', '_')
                metadata[key] = meta_match.group('value').strip().strip('`')
                continue

            if stripped == '## Development Status':
                in_dev_section = True
                continue

            if not in_dev_section:
                continue

            epic_match = _EPIC_HEADING_RE.match(stripped)
            if epic_match:
                current_epic = epic_match.group('epic')
                continue

            row_match = _TABLE_ROW_RE.match(stripped)
            if not row_match:
                continue

            left = row_match.group('left').strip()
            right = row_match.group('right').strip()
            if left.lower() == 'story' or set(left) == {'-'}:
                continue

            key = self._markdown_row_to_key(left, current_epic)
            if key is None:
                continue
            entries.append(
                SprintStatusEntry(
                    key=key,
                    entry_type=self._classify_entry(key),
                    status=self._normalize_status(right),
                )
            )

        return metadata, entries

    def _load_structured_payload(self, text: str) -> dict:
        candidates = [text, self._extract_yaml_block(text), self._repair_nested_status_keys(text)]
        repaired = self._repair_nested_status_keys(self._extract_yaml_block(text))
        candidates.append(repaired)

        for candidate in candidates:
            if not candidate.strip():
                continue
            try:
                payload = yaml.safe_load(candidate) or {}
            except Exception:
                continue
            if isinstance(payload, dict):
                return payload
        return {}

    def _extract_metadata(self, payload: dict) -> dict:
        metadata_source = payload.get('metadata') if isinstance(payload.get('metadata'), dict) else payload
        return {
            'generated': metadata_source.get('generated'),
            'project': metadata_source.get('project'),
            'project_key': metadata_source.get('project_key'),
            'tracking_system': metadata_source.get('tracking_system'),
            'story_location': metadata_source.get('story_location'),
        }

    def _extract_entries(self, payload: dict) -> list[SprintStatusEntry]:
        entries: list[SprintStatusEntry] = []
        development_status = payload.get('development_status', {}) or {}
        if isinstance(development_status, dict):
            for key, status in development_status.items():
                normalized_key = self._normalize_story_key(str(key))
                entries.append(
                    SprintStatusEntry(
                        key=normalized_key,
                        entry_type=self._classify_entry(normalized_key),
                        status=self._normalize_status(str(status)),
                    )
                )
            if entries:
                return entries

        sprints = payload.get('sprints', {}) or {}
        if isinstance(sprints, list):
            sprint_items = sprints
        elif isinstance(sprints, dict):
            sprint_items = list(sprints.values())
        else:
            sprint_items = []

        for sprint in sprint_items:
            if not isinstance(sprint, dict):
                continue
            for story in sprint.get('stories', []) or []:
                if not isinstance(story, dict):
                    continue
                story_id = story.get('id')
                if story_id is None:
                    continue
                key = self._normalize_story_key(str(story_id))
                entries.append(
                    SprintStatusEntry(
                        key=key,
                        entry_type='story',
                        status=self._normalize_status(str(story.get('status', 'backlog'))),
                    )
                )
        return entries

    def _extract_yaml_block(self, text: str) -> str:
        lines = text.splitlines()
        start = None
        for index, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            if re.match(r'^[A-Za-z0-9_-]+:\s*', stripped):
                start = index
                break
        if start is None:
            return ''

        collected: list[str] = []
        for line in lines[start:]:
            stripped = line.strip()
            if collected and stripped.startswith('# ') and not line.startswith(' '):
                break
            collected.append(line)
        return '\n'.join(collected).strip() + '\n'

    def _extract_line_oriented_entries(self, text: str) -> list[SprintStatusEntry]:
        story_entries = self._extract_story_block_entries(text)
        if story_entries:
            return story_entries
        return self._extract_sprint_story_id_entries(text)

    def _extract_story_block_entries(self, text: str) -> list[SprintStatusEntry]:
        entries: list[SprintStatusEntry] = []
        current_story_id: str | None = None

        def flush(status_value: str | None) -> None:
            nonlocal current_story_id
            if current_story_id and status_value:
                entries.append(
                    SprintStatusEntry(
                        key=self._normalize_story_key(current_story_id),
                        entry_type='story',
                        status=self._normalize_status(status_value),
                    )
                )
            current_story_id = None

        for line in text.splitlines():
            story_match = re.match(r'^\s*-\s+id:\s*(.+?)\s*$', line)
            if story_match:
                flush(None)
                current_story_id = story_match.group(1).strip().strip('"\'')
                continue
            if current_story_id:
                status_match = re.match(r'^\s+status:\s*(.+?)\s*$', line)
                if status_match:
                    flush(status_match.group(1).strip().strip('"\''))
        return entries

    def _extract_sprint_story_id_entries(self, text: str) -> list[SprintStatusEntry]:
        entries: list[SprintStatusEntry] = []
        current_story_ids: list[str] = []
        current_status: str | None = None
        collecting_story_ids = False
        active_sprint = False

        def flush() -> None:
            nonlocal current_story_ids, current_status, collecting_story_ids, active_sprint
            if current_story_ids and current_status:
                normalized_status = self._normalize_status(current_status)
                for story_id in current_story_ids:
                    entries.append(
                        SprintStatusEntry(
                            key=self._normalize_story_key(story_id),
                            entry_type='story',
                            status=normalized_status,
                        )
                    )
            current_story_ids = []
            current_status = None
            collecting_story_ids = False
            active_sprint = False

        for line in text.splitlines():
            sprint_match = re.match(r'^\s{2}sprint-[^:]+:\s*(?:.+)?$', line)
            if sprint_match:
                flush()
                active_sprint = True
                continue
            if not active_sprint:
                continue
            if re.match(r'^\s{2}[A-Za-z0-9_-]+:\s*', line) and not re.match(r'^\s{4}', line):
                flush()
                continue
            if line.strip() == 'story_ids:':
                collecting_story_ids = True
                continue
            if collecting_story_ids:
                story_id_match = re.match(r'^\s*-\s+([A-Za-z0-9-]+)\s*$', line)
                if story_id_match:
                    current_story_ids.append(story_id_match.group(1))
                    continue
                collecting_story_ids = False
            status_match = re.match(r'^\s+status:\s*(.+?)\s*$', line)
            if status_match:
                current_status = status_match.group(1).strip().strip('"\'')
        flush()
        return entries

    def _repair_nested_status_keys(self, text: str) -> str:
        lines = text.splitlines()
        repaired: list[str] = []
        for index, line in enumerate(lines):
            match = _INVALID_NESTED_KEY_RE.match(line)
            if not match:
                repaired.append(line)
                continue
            indent = match.group('indent')
            next_non_empty = None
            for future in lines[index + 1:]:
                if future.strip():
                    next_non_empty = future
                    break
            if next_non_empty and len(next_non_empty) - len(next_non_empty.lstrip(' ')) > len(indent):
                repaired.append(f"{indent}{match.group('key')}:")
                continue
            repaired.append(line)
        return '\n'.join(repaired)

    def _markdown_row_to_key(self, label: str, current_epic: str | None) -> str | None:
        cleaned = label.replace('**', '').strip().strip('`')
        if not cleaned:
            return None
        story_match = re.match(r'^(\d+-\d+(?:-[a-z0-9-]+)?)$', cleaned)
        if story_match:
            return cleaned
        if cleaned.lower().endswith('retrospective') and current_epic:
            return f'epic-{current_epic}-retrospective'
        return None

    @staticmethod
    def _normalize_story_key(key: str) -> str:
        stripped = key.strip()
        dotted = _STORY_ID_DOTTED_RE.match(stripped)
        if dotted:
            return f"{dotted.group('epic')}-{dotted.group('story')}"
        short = _STORY_ID_SHORT_RE.match(stripped)
        if short:
            return f"{short.group('epic')}-{short.group('story')}"
        return stripped

    @staticmethod
    def _normalize_status(status: str) -> str:
        cleaned = re.sub(r'^[^A-Za-z0-9]+', '', status.strip()).lower()
        cleaned = cleaned.replace('✅', '').strip()
        alias_map = {
            'complete': 'done',
            'completed': 'done',
            'dev_complete': 'done',
            'spec_created': 'backlog',
            'pending': 'backlog',
            'ready-for-qa': 'review',
            'reviewed': 'review',
            'code-review-remediated': 'review',
        }
        return alias_map.get(cleaned, cleaned)

    @staticmethod
    def _classify_entry(key: str) -> str:
        if key.startswith('epic-') and key.endswith('-retrospective'):
            return 'retrospective'
        if key.startswith('epic-'):
            return 'epic'
        return 'story'
