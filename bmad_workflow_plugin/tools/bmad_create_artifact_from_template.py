from __future__ import annotations

from bmad_workflow_plugin.schemas.bmad_create_artifact_from_template import (
    BmadCreateArtifactFromTemplateRequest,
    BmadCreateArtifactFromTemplateResponse,
    BmadBmadCreateArtifactFromTemplateResponseData,
)
from bmad_workflow_plugin.schemas.common import Message


class BmadCreateArtifactFromTemplateTool:
    def __init__(self, artifact_service) -> None:
        self.artifact_service = artifact_service

    def execute(self, request: BmadCreateArtifactFromTemplateRequest | dict) -> BmadCreateArtifactFromTemplateResponse:
        if isinstance(request, dict):
            request = BmadCreateArtifactFromTemplateRequest(**request)
        try:
            result = self.artifact_service.create_from_template(
                project_root=request.project_root,
                artifact_type=request.artifact_type.value,
                template_vars=request.template_vars,
                inventory=request.inventory,
                destination_path=request.destination_path,
                overwrite=request.overwrite,
            )
            return BmadCreateArtifactFromTemplateResponse(
                success=True,
                data=BmadBmadCreateArtifactFromTemplateResponseData(
                    artifact_type=result['artifact_type'],
                    artifact_path=result['path'],
                    created=True,
                    used_template=result['template_used'],
                    validation=result['validation_result'],
                ),
            )
        except Exception as e:
            return BmadCreateArtifactFromTemplateResponse(
                success=False,
                data=None,
                errors=[Message(code='create_artifact_error', message=str(e))],
            )
