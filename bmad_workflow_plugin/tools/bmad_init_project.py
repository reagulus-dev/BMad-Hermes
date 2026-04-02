from __future__ import annotations

from bmad_workflow_plugin.schemas.bmad_init_project import (
    BmadInitProjectRequest,
    BmadInitProjectResponse,
    BmadInitProjectResponseData,
)
from bmad_workflow_plugin.schemas.common import Message


class BmadInitProjectTool:
    def __init__(self, init_service) -> None:
        self.init_service = init_service

    def execute(self, request: BmadInitProjectRequest | dict) -> BmadInitProjectResponse:
        if isinstance(request, dict):
            request = BmadInitProjectRequest(**request)
        try:
            result = self.init_service.init_project(
                project_root=request.project_root,
                project_name=request.project_name,
                create_core_config=request.create_core_config,
                output_folder=request.output_folder,
                user_name=request.user_name,
                communication_language=request.communication_language,
                document_output_language=request.document_output_language,
                user_skill_level=request.user_skill_level,
            )
            return BmadInitProjectResponse(
                success=True,
                data=BmadInitProjectResponseData(**result),
            )
        except Exception as e:
            return BmadInitProjectResponse(
                success=False,
                data=None,
                errors=[Message(code='init_project_error', message=str(e))],
            )
