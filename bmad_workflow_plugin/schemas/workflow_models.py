from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class WorkflowInfo:
    workflow_id: str
    display_name: str
    phase: str
    status_triggers: list[str]
    recommended_skill: str
    required: bool
    description: str
    long_description: str | None = None
    outputs: list[str] = field(default_factory=list)
    after: list[str] = field(default_factory=list)
    before: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RoutingDecision:
    next_workflow_id: str
    recommended_skill: str
    reason: str
    blocked: bool
    blockers: list[str] = field(default_factory=list)
    target_story_key: str | None = None
    phase: str | None = None


@dataclass(slots=True)
class BmadWorkflowHelpResponse:
    workflow_id: str
    display_name: str
    description: str
    recommended_skill: str
    phase: str
    required: bool
    outputs: list[str] = field(default_factory=list)
    after: list[str] = field(default_factory=list)
    before: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)


@dataclass(slots=True)
class BmadNextWorkflowResponse:
    success: bool
    decision: RoutingDecision | None
    available_workflows: list[WorkflowInfo] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
