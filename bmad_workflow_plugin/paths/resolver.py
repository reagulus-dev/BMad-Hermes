from __future__ import annotations

from dataclasses import dataclass, field
import glob
from pathlib import Path
import re
from typing import Any

from bmad_workflow_plugin.registry.models import ArtifactContract
from bmad_workflow_plugin.state.bmad_config import BmadConfigReader


@dataclass(slots=True)
class ResolvedPath:
    path: str | None
    source_kind: str | None
    candidates: list[str] = field(default_factory=list)
    ambiguous: bool = False


class PathResolver:
    def __init__(self, registry: dict[str, ArtifactContract] | None = None) -> None:
        self.registry = registry or {}
        self.config_reader = BmadConfigReader()

    def resolve_artifact_path(self, project_root: str, artifact_type: str, identity: dict | None = None) -> ResolvedPath:
        candidates = self._candidate_paths(project_root, artifact_type, identity)
        existing: list[tuple[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for source_kind, path in candidates:
            if Path(path).exists():
                item = (source_kind, path)
                if item not in seen:
                    existing.append(item)
                    seen.add(item)

        for source_kind, pattern in self._glob_patterns(project_root, artifact_type, identity):
            for path in sorted(glob.glob(pattern)):
                item = (source_kind, str(Path(path).resolve()))
                if item not in seen:
                    existing.append(item)
                    seen.add(item)

        if not existing:
            return ResolvedPath(path=None, source_kind=None, candidates=[p for _, p in candidates], ambiguous=False)

        # If more than one location has the file, it's ambiguous regardless of kind.
        # The caller must reconcile before we can safely pick one.
        if len(existing) > 1:
            return ResolvedPath(path=None, source_kind=None, candidates=[p for _, p in existing], ambiguous=True)
        # Exactly one location has the file — unambiguous.
        item = existing[0]
        return ResolvedPath(path=item[1], source_kind=item[0], candidates=[item[1]], ambiguous=False)

    def build_preferred_path(self, project_root: str, artifact_type: str, identity: dict | None = None) -> str:
        candidates = self._candidate_paths(project_root, artifact_type, identity)
        for source_kind, path in candidates:
            if source_kind == 'preferred':
                return path
        raise KeyError(f'No preferred path configured for artifact_type={artifact_type}')

    def _candidate_paths(self, project_root: str, artifact_type: str, identity: dict | None) -> list[tuple[str, str]]:
        contract = self.registry.get(artifact_type)
        if not contract:
            raise KeyError(f'Unknown artifact type: {artifact_type}')
        raw = contract.raw if hasattr(contract, 'raw') else contract
        path_resolution = raw.get('path_resolution', {})
        identity = self._enrich_identity(project_root, identity)
        project_root = str(Path(project_root).resolve())
        legacy_root = self._legacy_output_root(project_root)

        def materialize(template: str, source_kind: str) -> str:
            template = self._rewrite_legacy_template(template, source_kind, legacy_root)
            rendered = template
            for key, value in identity.items():
                rendered = rendered.replace('{' + key + '}', str(value))
            # collapse unresolved placeholders conservatively
            rendered = re.sub(r'\{[^{}]+\}', 'UNRESOLVED', rendered)
            return str((Path(project_root) / rendered).resolve())

        out: list[tuple[str, str]] = []
        for source_kind in ('preferred', 'legacy_compatible'):
            for template in path_resolution.get(source_kind, []) or []:
                out.append((source_kind, materialize(template, source_kind)))
        return out

    def _glob_patterns(self, project_root: str, artifact_type: str, identity: dict | None) -> list[tuple[str, str]]:
        contract = self.registry.get(artifact_type)
        if not contract:
            raise KeyError(f'Unknown artifact type: {artifact_type}')
        raw = contract.raw if hasattr(contract, 'raw') else contract
        path_resolution = raw.get('path_resolution', {})
        identity = self._enrich_identity(project_root, identity)
        project_root = str(Path(project_root).resolve())
        legacy_root = self._legacy_output_root(project_root)

        patterns: list[tuple[str, str]] = []
        for source_kind in ('preferred', 'legacy_compatible'):
            for template in path_resolution.get(source_kind, []) or []:
                template = self._rewrite_legacy_template(template, source_kind, legacy_root)
                rendered = template
                for key, value in identity.items():
                    rendered = rendered.replace('{' + key + '}', str(value))
                if '{' not in rendered:
                    continue
                rendered = re.sub(r'\{([^{}]+)\}', self._placeholder_glob, rendered)
                patterns.append((source_kind, str((Path(project_root) / rendered).resolve())))
        return patterns

    @staticmethod
    def _placeholder_glob(match: re.Match[str]) -> str:
        name = match.group(1).strip().lower()
        if 'version' in name:
            return '[0-9]*'
        return '*'

    def _enrich_identity(self, project_root: str, identity: dict | None) -> dict[str, Any]:
        identity_out: dict[str, Any] = dict(identity or {})
        config = self.config_reader.read(project_root) or {}
        if config.get('project_name') and not identity_out.get('project_name'):
            identity_out['project_name'] = config['project_name']

        story_key = str(identity_out.get('story_key') or '').strip()
        if story_key:
            identity_out.setdefault('story_key_legacy', story_key if story_key.startswith('story-') else f'story-{story_key}')
            short_key_match = re.match(r'^(?:story-)?(?P<epic>\d+)[-.](?P<story>\d+)', story_key)
            if short_key_match:
                short_key = f"{short_key_match.group('epic')}-{short_key_match.group('story')}"
                identity_out.setdefault('story_key_short', short_key)
        return identity_out

    def _legacy_output_root(self, project_root: str) -> str:
        output_folder = self.config_reader.output_folder(project_root)
        return output_folder.strip('/').rstrip('/')

    @staticmethod
    def _rewrite_legacy_template(template: str, source_kind: str, legacy_root: str) -> str:
        if source_kind != 'legacy_compatible':
            return template
        if template.startswith('_bmad-output/'):
            return template.replace('_bmad-output/', legacy_root + '/', 1)
        if template == '_bmad-output':
            return legacy_root
        return template
