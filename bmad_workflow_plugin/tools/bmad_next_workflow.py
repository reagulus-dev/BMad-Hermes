from __future__ import annotations

from bmad_workflow_plugin.schemas.bmad_next_workflow import (
    BmadNextWorkflowRequest,
    BmadNextWorkflowResponse,
    BmadBmadNextWorkflowResponseData,
)
from bmad_workflow_plugin.schemas.workflow_models import RoutingDecision, WorkflowInfo
from bmad_workflow_plugin.schemas.common import Message


class BmadNextWorkflowTool:
    def __init__(self, workflow_service) -> None:
        self.workflow_service = workflow_service

    def execute(self, request: BmadNextWorkflowRequest | dict) -> BmadNextWorkflowResponse:
        if isinstance(request, dict):
            request = BmadNextWorkflowRequest(**request)
        try:
            result = self.workflow_service.next_workflow(
                project_root=request.project_root,
                target_story_key=request.target_story_key,
            )
            decision = RoutingDecision(
                next_workflow_id=result['next_workflow_id'],
                recommended_skill=result['recommended_skill'],
                reason=result['reason'],
                blocked=result['blocked'],
                blockers=result['blockers'],
                target_story_key=result.get('target_story_key'),
                phase=result.get('phase'),
            )
            workflows = self.workflow_service.list_workflows()
            infos = [
                WorkflowInfo(
                    workflow_id=w['workflow_id'],
                    display_name=w['display_name'],
                    phase=w['phase'],
                    status_triggers=w['status_triggers'],
                    recommended_skill=w['recommended_skill'],
                    required=w['required'],
                    description=w['description'],
                    outputs=w['outputs'],
                    after=w['after'],
                    before=w['before'],
                )
                for w in workflows
            ]
            return BmadNextWorkflowResponse(
                success=True,
                data=BmadBmadNextWorkflowResponseData(
                    project_root=request.project_root,
                    decision=decision,
                    available_workflows=infos,
                ),
            )
        except Exception as e:
            return BmadNextWorkflowResponse(
                success=False,
                data=None,
                errors=[Message(code='next_workflow_error', message=str(e))],
            )
