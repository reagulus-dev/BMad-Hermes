from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

from .models import ArtifactContract

# The directory containing this loader — used as base for relative template paths
_PLUGIN_DIR = Path(__file__).resolve().parent.parent


class RegistryLoader:
    def __init__(self, registry_path: str | None = None) -> None:
        default = Path(__file__).with_name('artifact_contracts.yaml')
        self.registry_path = Path(registry_path) if registry_path else default
        self._contracts: dict[str, ArtifactContract] = {}
        self._raw_registry: dict[str, Any] | None = None

    def load_default(self) -> dict[str, ArtifactContract]:
        return self.load()

    def load(self) -> dict[str, ArtifactContract]:
        with self.registry_path.open('r', encoding='utf-8') as f:
            payload = yaml.safe_load(f) or {}
        artifact_types = payload.get('artifact_types', {})
        contracts: dict[str, ArtifactContract] = {}
        for artifact_type, raw in artifact_types.items():
            raw = dict(raw)
            # Resolve relative template paths against the plugin directory
            templates = raw.get('source_templates', {})
            if isinstance(templates, dict):
                for tmpl in templates.values():
                    if isinstance(tmpl, dict) and 'path' in tmpl:
                        p = tmpl['path']
                        if p and not Path(p).is_absolute():
                            tmpl['path'] = str(_PLUGIN_DIR / p)
            contracts[artifact_type] = ArtifactContract(
                artifact_type=artifact_type,
                contract_version=str(raw.get('contract_version', '0.0.0')),
                display_name=str(raw.get('display_name', artifact_type)),
                phase=str(raw.get('phase', 'unknown')),
                format=str(raw.get('format', 'unknown')),
                raw=raw,
            )
        self._contracts = contracts
        self._raw_registry = payload
        return contracts

    def get_contract(self, artifact_type: str) -> ArtifactContract:
        if not self._contracts:
            self.load()
        try:
            return self._contracts[artifact_type]
        except KeyError as e:
            raise KeyError(f"Unknown artifact type: {artifact_type}") from e

    @property
    def raw_registry(self) -> dict[str, Any]:
        if self._raw_registry is None:
            self.load()
        return self._raw_registry or {}
