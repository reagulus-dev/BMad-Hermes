from __future__ import annotations
from dataclasses import dataclass, field
from bmad_workflow_plugin.schemas.common import ArtifactType, WorkflowId, StoryStatus, Message, ValidationResult

@dataclass(slots=True)
class SetFieldOperation:
    op: str
    field: str
    value: str

@dataclass(slots=True)
class ReplaceSectionOperation:
    op: str
    section: str
    content: str

@dataclass(slots=True)
class AppendSectionOperation:
    op: str
    section: str
    content: str

@dataclass(slots=True)
class CheckCheckboxOperation:
    op: str
    section: str
    match_text: str
    checked: bool

@dataclass(slots=True)
class BmadUpdateArtifactSectionRequest:
    project_root: str
    artifact_type: ArtifactType
    artifact_path: str
    workflow_id: WorkflowId
    operations: list[object]

@dataclass(slots=True)
class BmadBmadUpdateArtifactSectionResponseData:
    artifact_type: str
    artifact_path: str
    applied_operations: int
    validation: ValidationResult
    updated_summary: dict

@dataclass(slots=True)
class BmadUpdateArtifactSectionResponse:
    success: bool
    data: BmadBmadUpdateArtifactSectionResponseData | None
    warnings: list[Message] = field(default_factory=list)
    errors: list[Message] = field(default_factory=list)
