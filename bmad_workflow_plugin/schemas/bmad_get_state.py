from __future__ import annotations
from dataclasses import dataclass, field
from bmad_workflow_plugin.schemas.artifact_models import NormalizedState
from bmad_workflow_plugin.schemas.common import Message

@dataclass(slots=True)
class BmadGetStateRequest:
    project_root: str

@dataclass(slots=True)
class BmadGetStateResponse:
    success: bool
    data: NormalizedState | None
    warnings: list[Message] = field(default_factory=list)
    errors: list[Message] = field(default_factory=list)
