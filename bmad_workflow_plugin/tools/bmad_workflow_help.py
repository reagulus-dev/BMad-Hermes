from __future__ import annotations

from bmad_workflow_plugin.schemas.bmad_workflow_help import (
    BmadWorkflowHelpRequest,
    BmadWorkflowHelpResponse,
    BmadBmadWorkflowHelpResponseData,
)
from bmad_workflow_plugin.schemas.workflow_models import WorkflowInfo
from bmad_workflow_plugin.schemas.common import Message


class BmadWorkflowHelpTool:
    def __init__(self, workflow_service) -> None:
        self.workflow_service = workflow_service

    def execute(self, request: BmadWorkflowHelpRequest | dict) -> BmadWorkflowHelpResponse:
        if isinstance(request, dict):
            request = BmadWorkflowHelpRequest(**request)

        try:
            if request.list_all:
                return self._list_all(request)
            elif request.workflow_id:
                return self._get_one(request)
            elif request.phase:
                return self._list_by_phase(request)
            else:
                return BmadWorkflowHelpResponse(
                    success=False,
                    data=None,
                    errors=[Message(
                        code='invalid_request',
                        message='Provide workflow_id, phase, or list_all=true.'
                    )],
                )
        except Exception as e:
            return BmadWorkflowHelpResponse(
                success=False,
                data=None,
                errors=[Message(code='workflow_help_error', message=str(e))],
            )

    def _get_one(self, request: BmadWorkflowHelpRequest) -> BmadWorkflowHelpResponse:
        wf = self.workflow_service.get_workflow(request.workflow_id)
        if wf is None:
            return BmadWorkflowHelpResponse(
                success=False,
                data=None,
                errors=[Message(
                    code='not_found',
                    message=f"Workflow '{request.workflow_id}' not found."
                )],
            )
        return BmadWorkflowHelpResponse(
            success=True,
            data=BmadBmadWorkflowHelpResponseData(
                workflow_id=wf['workflow_id'],
                display_name=wf['display_name'],
                description=wf['description'],
                recommended_skill=wf['recommended_skill'],
                phase=wf['phase'],
                required=wf['required'],
                outputs=wf['outputs'],
                after=wf['after'],
                before=wf['before'],
                aliases=wf['aliases'],
            ),
        )

    def _list_all(self, request: BmadWorkflowHelpRequest) -> BmadWorkflowHelpResponse:
        workflows = self.workflow_service.list_workflows()
        infos = self._to_infos(workflows)
        return BmadWorkflowHelpResponse(
            success=True,
            data=BmadBmadWorkflowHelpResponseData(available_workflows=infos),
        )

    def _list_by_phase(self, request: BmadWorkflowHelpRequest) -> BmadWorkflowHelpResponse:
        workflows = self.workflow_service.list_workflows(request.phase)
        infos = self._to_infos(workflows)
        return BmadWorkflowHelpResponse(
            success=True,
            data=BmadBmadWorkflowHelpResponseData(available_workflows=infos),
        )

    @staticmethod
    def _to_infos(workflows: list[dict]) -> list[WorkflowInfo]:
        return [
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
