from __future__ import annotations
from dataclasses import dataclass, field
from bmad_workflow_plugin.schemas.workflow_models import RoutingDecision, WorkflowInfo
from bmad_workflow_plugin.schemas.common import Message

@dataclass(slots=True)
class BmadNextWorkflowRequest:
    project_root: str
    target_story_key: str | None = None

@dataclass(slots=True)
class BmadBmadNextWorkflowResponseData:
    project_root: str
    decision: RoutingDecision
    available_workflows: list[WorkflowInfo]

@dataclass(slots=True)
class BmadNextWorkflowResponse:
    success: bool
    data: BmadBmadNextWorkflowResponseData | None
    warnings: list[Message] = field(default_factory=list)
    errors: list[Message] = field(default_factory=list)
