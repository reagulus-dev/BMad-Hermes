from __future__ import annotations

from bmad_workflow_plugin.schemas.bmad_validate_artifact import (
    BmadValidateArtifactRequest,
    BmadValidateArtifactResponse,
    BmadBmadValidateArtifactResponseData,
)
from bmad_workflow_plugin.schemas.common import Message


class BmadValidateArtifactTool:
    def __init__(self, artifact_service) -> None:
        self.artifact_service = artifact_service

    def execute(self, request: BmadValidateArtifactRequest | dict) -> BmadValidateArtifactResponse:
        if isinstance(request, dict):
            request = BmadValidateArtifactRequest(**request)
        try:
            result = self.artifact_service.validate_artifact(
                project_root=request.project_root,
                artifact_type=request.artifact_type.value,
                artifact_path=request.artifact_path,
            )
            return BmadValidateArtifactResponse(
                success=True,
                data=BmadBmadValidateArtifactResponseData(
                    artifact_type=result['artifact_type'],
                    artifact_path=result['artifact_path'],
                    valid=result['valid'],
                    validation=result['validation_result'],
                ),
            )
        except Exception as e:
            return BmadValidateArtifactResponse(
                success=False,
                data=None,
                errors=[Message(code='validate_artifact_error', message=str(e))],
            )
