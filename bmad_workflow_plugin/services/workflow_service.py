from __future__ import annotations

from typing import Any, Callable

from bmad_workflow_plugin.routing.workflow_router import WorkflowRouter


Factory = Callable[[], Any]


class WorkflowService:
    def __init__(self, router_factory: Factory | None = None) -> None:
        self._router_factory = router_factory or WorkflowRouter
        self._router = None

    def _get_router(self) -> WorkflowRouter:
        if self._router is None:
            self._router = self._router_factory()
        return self._router

    def next_workflow(self, project_root: str, target_story_key: str | None = None) -> dict:
        """
        Compute the next workflow recommendation.
        Returns a RoutingDecision as dict with keys:
          next_workflow_id, recommended_skill, reason, blocked, blockers, target_story_key, phase
        """
        decision = self._get_router().next_workflow(project_root, target_story_key)
        return {
            'next_workflow_id': decision.next_workflow_id,
            'recommended_skill': decision.recommended_skill,
            'reason': decision.reason,
            'blocked': decision.blocked,
            'blockers': decision.blockers,
            'target_story_key': decision.target_story_key,
            'phase': decision.phase,
        }

    def get_workflow(self, workflow_id: str) -> dict | None:
        """Return a workflow entry by ID or alias."""
        wf = self._get_router().get_workflow(workflow_id)
        if wf is None:
            return None
        return {
            'workflow_id': wf.workflow_id,
            'display_name': wf.display_name,
            'phase': wf.phase,
            'status_triggers': wf.status_triggers,
            'recommended_skill': wf.recommended_skill,
            'required': wf.required,
            'description': wf.description,
            'outputs': wf.outputs,
            'after': wf.after,
            'before': wf.before,
            'aliases': wf.aliases,
        }

    def list_workflows(self, phase: str | None = None) -> list[dict]:
        """List all workflows, optionally filtered by phase."""
        router = self._get_router()
        if phase:
            workflows = router.list_workflows_by_phase(phase)
        else:
            workflows = router.all_workflows()
        return [
            {
                'workflow_id': w.workflow_id,
                'display_name': w.display_name,
                'phase': w.phase,
                'status_triggers': w.status_triggers,
                'recommended_skill': w.recommended_skill,
                'required': w.required,
                'description': w.description,
                'outputs': w.outputs,
                'after': w.after,
                'before': w.before,
                'aliases': w.aliases,
            }
            for w in workflows
        ]
