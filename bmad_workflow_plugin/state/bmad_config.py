from __future__ import annotations

from pathlib import Path
import yaml


class BmadConfigReader:
    """Read BMad upstream/exported project config from supported _bmad config locations."""

    def read(self, project_root: str) -> dict | None:
        for path in self._candidate_paths(project_root):
            if not path.exists():
                continue
            with path.open('r', encoding='utf-8') as f:
                payload = yaml.safe_load(f) or {}
            if isinstance(payload, dict):
                return payload
        return None

    @staticmethod
    def _candidate_paths(project_root: str) -> list[Path]:
        root = Path(project_root)
        return [
            root / '_bmad' / 'core' / 'config.yaml',
            root / '_bmad' / 'config.yaml',
        ]

    def output_folder(self, project_root: str) -> str:
        config = self.read(project_root) or {}
        value = config.get('output_folder') or '_bmad-output'
        return str(value).strip() or '_bmad-output'
