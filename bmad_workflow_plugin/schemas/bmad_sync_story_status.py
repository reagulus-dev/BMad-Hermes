from __future__ import annotations
from dataclasses import dataclass, field
from bmad_workflow_plugin.schemas.common import WorkflowId, StoryStatus, Message, UpdateResult

@dataclass(slots=True)
class BmadSyncStoryStatusRequest:
    project_root: str
    story_key: str
    new_status: StoryStatus
    source_workflow: WorkflowId
    reason: str | None = None

@dataclass(slots=True)
class BmadBmadSyncStoryStatusResponseData:
    story_key: str
    new_status: str
    source_workflow: str
    updates: dict[str, UpdateResult]

@dataclass(slots=True)
class BmadSyncStoryStatusResponse:
    success: bool
    data: BmadBmadSyncStoryStatusResponseData | None
    warnings: list[Message] = field(default_factory=list)
    errors: list[Message] = field(default_factory=list)
