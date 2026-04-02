from __future__ import annotations
from dataclasses import dataclass, field
from bmad_workflow_plugin.schemas.workflow_models import WorkflowInfo
from bmad_workflow_plugin.schemas.common import Message

@dataclass(slots=True)
class BmadWorkflowHelpRequest:
    workflow_id: str | None = None
    phase: str | None = None
    list_all: bool = False

@dataclass(slots=True)
class BmadBmadWorkflowHelpResponseData:
    workflow_id: str | None = None
    display_name: str | None = None
    description: str | None = None
    recommended_skill: str | None = None
    phase: str | None = None
    required: bool = False
    outputs: list[str] = field(default_factory=list)
    after: list[str] = field(default_factory=list)
    before: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    available_workflows: list[WorkflowInfo] = field(default_factory=list)

@dataclass(slots=True)
class BmadWorkflowHelpResponse:
    success: bool
    data: BmadBmadWorkflowHelpResponseData | None
    warnings: list[Message] = field(default_factory=list)
    errors: list[Message] = field(default_factory=list)
