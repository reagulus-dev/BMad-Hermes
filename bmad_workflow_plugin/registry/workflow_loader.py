from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

from .workflow_models import WorkflowEntry, WorkflowRegistry

_PLUGIN_DIR = Path(__file__).resolve().parent.parent


class WorkflowRegistryLoader:
    def __init__(self, registry_path: str | None = None) -> None:
        default = Path(__file__).with_name('workflow_registry.yaml')
        self.registry_path = Path(registry_path) if registry_path else default
        self._registry: WorkflowRegistry | None = None
        self._raw: dict[str, Any] | None = None

    def load(self) -> WorkflowRegistry:
        if self._registry is not None:
            return self._registry

        with self.registry_path.open('r', encoding='utf-8') as f:
            payload = yaml.safe_load(f) or {}

        global_defaults = payload.get('global_defaults', {})
        workflows_raw: dict[str, Any] = payload.get('workflows', {})

        workflows: dict[str, WorkflowEntry] = {}
        for workflow_id, raw in workflows_raw.items():
            raw = dict(raw)
            workflows[workflow_id] = WorkflowEntry(
                workflow_id=workflow_id,
                display_name=str(raw.get('display_name', workflow_id)),
                phase=str(raw.get('phase', global_defaults.get('default_phase', '4-implementation'))),
                status_triggers=raw.get('status_triggers', []),
                allowed_from=raw.get('allowed_from', []),
                recommended_skill=str(raw.get('recommended_skill', '')),
                required=bool(raw.get('required', False)),
                description=str(raw.get('description', '')),
                long_description=raw.get('long_description'),
                outputs=raw.get('outputs', []),
                after=raw.get('after', []),
                before=raw.get('before', []),
                aliases=raw.get('aliases', []),
                raw=raw,
            )

        self._registry = WorkflowRegistry(
            registry_version=str(payload.get('registry_version', '0.0.0')),
            registry_id=str(payload.get('registry_id', '')),
            workflows=workflows,
        )
        self._raw = payload
        return self._registry

    def get(self, workflow_id: str) -> WorkflowEntry | None:
        return self.load().get(workflow_id)

    def get_workflows_for_status(self, status: str) -> list[WorkflowEntry]:
        """Return all workflows that can be triggered by a given story status."""
        return self.load().by_status_trigger(status)

    def get_next_workflows(self, from_workflow_id: str) -> list[WorkflowEntry]:
        """Return workflows that can follow a given workflow."""
        return self.load().next_workflows(from_workflow_id)

    def all_workflows(self) -> list[WorkflowEntry]:
        return list(self.load().workflows.values())

    def by_phase(self, phase: str) -> list[WorkflowEntry]:
        return self.load().by_phase(phase)

    @property
    def raw_registry(self) -> dict[str, Any]:
        if self._raw is None:
            self.load()
        return self._raw or {}
