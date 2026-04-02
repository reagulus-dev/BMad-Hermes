from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from bmad_workflow_plugin.schemas.common import ArtifactType, Message, ValidationResult

@dataclass(slots=True)
class BmadReadArtifactRequest:
    project_root: str
    artifact_type: ArtifactType
    artifact_path: str | None = None

@dataclass(slots=True)
class BmadBmadReadArtifactResponseData:
    artifact_type: str
    artifact_path: str
    parsed: Any
    validation: ValidationResult

@dataclass(slots=True)
class BmadReadArtifactResponse:
    success: bool
    data: BmadBmadReadArtifactResponseData | None
    warnings: list[Message] = field(default_factory=list)
    errors: list[Message] = field(default_factory=list)
