from __future__ import annotations
from dataclasses import dataclass, field
from bmad_workflow_plugin.schemas.common import ArtifactType, Message, ValidationResult

@dataclass(slots=True)
class BmadValidateArtifactRequest:
    project_root: str
    artifact_type: ArtifactType
    artifact_path: str | None = None

@dataclass(slots=True)
class BmadBmadValidateArtifactResponseData:
    artifact_type: str
    artifact_path: str
    valid: bool
    validation: ValidationResult

@dataclass(slots=True)
class BmadValidateArtifactResponse:
    success: bool
    data: BmadBmadValidateArtifactResponseData | None
    warnings: list[Message] = field(default_factory=list)
    errors: list[Message] = field(default_factory=list)
