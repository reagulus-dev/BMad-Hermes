from __future__ import annotations
from dataclasses import dataclass, field
from bmad_workflow_plugin.schemas.artifact_models import ArtifactContractSummary
from bmad_workflow_plugin.schemas.common import ArtifactType, Message

@dataclass(slots=True)
class BmadGetArtifactContractRequest:
    artifact_type: ArtifactType

@dataclass(slots=True)
class BmadBmadGetArtifactContractResponseData:
    """Alias wrapper kept for tool layer compatibility."""
    artifact_type: str
    summary: ArtifactContractSummary

@dataclass(slots=True)
class BmadGetArtifactContractResponse:
    success: bool
    data: ArtifactContractSummary | None
    warnings: list[Message] = field(default_factory=list)
    errors: list[Message] = field(default_factory=list)
