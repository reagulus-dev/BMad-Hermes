from __future__ import annotations

from bmad_workflow_plugin.schemas.bmad_get_state import BmadGetStateRequest, BmadGetStateResponse
from bmad_workflow_plugin.schemas.common import Message


class BmadGetStateTool:
    def __init__(self, state_service) -> None:
        self.state_service = state_service

    def execute(self, request: BmadGetStateRequest | dict) -> BmadGetStateResponse:
        if isinstance(request, dict):
            request = BmadGetStateRequest(**request)
        try:
            normalized = self.state_service.get_state(request.project_root)
            return BmadGetStateResponse(success=True, data=normalized)
        except Exception as e:
            return BmadGetStateResponse(
                success=False,
                data=None,
                errors=[Message(code='state_read_error', message=str(e))],
            )
