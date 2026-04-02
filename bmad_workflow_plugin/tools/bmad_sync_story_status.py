from __future__ import annotations

from bmad_workflow_plugin.schemas.bmad_sync_story_status import (
    BmadSyncStoryStatusRequest,
    BmadSyncStoryStatusResponse,
    BmadBmadSyncStoryStatusResponseData,
)
from bmad_workflow_plugin.schemas.common import Message, UpdateResult


class BmadSyncStoryStatusTool:
    def __init__(self, sync_service) -> None:
        self.sync_service = sync_service

    def execute(self, request: BmadSyncStoryStatusRequest | dict) -> BmadSyncStoryStatusResponse:
        if isinstance(request, dict):
            request = BmadSyncStoryStatusRequest(**request)
        try:
            result = self.sync_service.sync_story_status(
                project_root=request.project_root,
                story_key=request.story_key,
                new_status=request.new_status.value,
                source_workflow=request.source_workflow.value,
                reason=request.reason,
            )
            return BmadSyncStoryStatusResponse(
                success=True,
                data=BmadBmadSyncStoryStatusResponseData(
                    story_key=request.story_key,
                    new_status=request.new_status.value,
                    source_workflow=request.source_workflow.value,
                    updates={
                        'sprint_status': UpdateResult(
                            updated=True,
                            path=result['sprint_status_path'],
                            notes=result['notes'],
                        ),
                        'state': UpdateResult(
                            updated=True,
                            path=result['state_path'],
                            notes=[],
                        ),
                    },
                ),
            )
        except Exception as e:
            return BmadSyncStoryStatusResponse(
                success=False,
                data=None,
                errors=[Message(code='sync_error', message=str(e))],
            )
