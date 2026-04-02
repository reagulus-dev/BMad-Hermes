from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class WorkflowEntry:
    workflow_id: str
    display_name: str
    phase: str
    status_triggers: list[str]
    allowed_from: list[str]
    recommended_skill: str
    required: bool
    description: str
    long_description: str | None = None
    outputs: list[str] = field(default_factory=list)
    after: list[str] = field(default_factory=list)
    before: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WorkflowRegistry:
    registry_version: str
    registry_id: str
    workflows: dict[str, WorkflowEntry] = field(default_factory=dict)

    def get(self, workflow_id: str) -> WorkflowEntry | None:
        if workflow_id in self.workflows:
            return self.workflows[workflow_id]
        # Check aliases
        for entry in self.workflows.values():
            if workflow_id in entry.aliases:
                return entry
        return None

    def by_phase(self, phase: str) -> list[WorkflowEntry]:
        return [w for w in self.workflows.values() if w.phase == phase]

    def by_status_trigger(self, status: str) -> list[WorkflowEntry]:
        return [w for w in self.workflows.values() if status in w.status_triggers]

    def next_workflows(self, from_workflow_id: str) -> list[WorkflowEntry]:
        """Return workflows that list from_workflow_id in their 'allowed_from' or 'before'."""
        candidates = set()
        for wf in self.workflows.values():
            if from_workflow_id in wf.allowed_from or from_workflow_id in wf.before:
                candidates.add(wf.workflow_id)
        return [self.workflows[wid] for wid in candidates if wid in self.workflows]
