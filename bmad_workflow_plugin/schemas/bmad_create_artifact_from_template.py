from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from bmad_workflow_plugin.schemas.common import ArtifactType, Message, ValidationResult

@dataclass(slots=True)
class BmadCreateArtifactFromTemplateRequest:
    project_root: str
    artifact_type: ArtifactType
    template_vars: dict[str, Any]
    inventory: dict[str, Any] | None = None
    destination_path: str | None = None
    overwrite: bool = False

@dataclass(slots=True)
class BmadBmadCreateArtifactFromTemplateResponseData:
    artifact_type: str
    artifact_path: str
    created: bool
    used_template: str
    validation: ValidationResult

@dataclass(slots=True)
class BmadCreateArtifactFromTemplateResponse:
    success: bool
    data: BmadBmadCreateArtifactFromTemplateResponseData | None
    warnings: list[Message] = field(default_factory=list)
    errors: list[Message] = field(default_factory=list)
