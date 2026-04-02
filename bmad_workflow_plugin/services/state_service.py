from __future__ import annotations

from bmad_workflow_plugin.schemas.artifact_models import NormalizedState
from bmad_workflow_plugin.state.state_reader import StateReader
from bmad_workflow_plugin.state.state_normalizer import StateNormalizer
from bmad_workflow_plugin.state.state_writer import StateWriter


class StateService:
    def __init__(self, registry) -> None:
        self.registry = registry
        self._reader = StateReader()
        self._normalizer = StateNormalizer()
        self._writer = StateWriter()

    def get_state(self, project_root: str) -> NormalizedState:
        raw = self._reader.read(project_root)
        return self._normalizer.normalize(project_root, raw)

    def patch_state(self, project_root: str, patch: dict) -> str:
        return self._writer.write_patch(project_root, patch)
