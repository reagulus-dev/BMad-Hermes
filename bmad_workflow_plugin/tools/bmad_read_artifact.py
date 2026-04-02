from __future__ import annotations

from bmad_workflow_plugin.schemas.bmad_read_artifact import (
    BmadReadArtifactRequest,
    BmadReadArtifactResponse,
    BmadBmadReadArtifactResponseData,
)
from bmad_workflow_plugin.schemas.common import Message


class BmadReadArtifactTool:
    def __init__(self, artifact_service) -> None:
        self.artifact_service = artifact_service

    def execute(self, request: BmadReadArtifactRequest | dict) -> BmadReadArtifactResponse:
        if isinstance(request, dict):
            request = BmadReadArtifactRequest(**request)
        try:
            result = self.artifact_service.read_artifact(
                project_root=request.project_root,
                artifact_type=request.artifact_type.value,
                artifact_path=request.artifact_path,
            )
            doc = result['doc']
            return BmadReadArtifactResponse(
                success=True,
                data=BmadBmadReadArtifactResponseData(
                    artifact_type=request.artifact_type.value,
                    artifact_path=doc.path,
                    parsed=doc,
                    validation=result['validation_result'],
                ),
            )
        except Exception as e:
            return BmadReadArtifactResponse(
                success=False,
                data=None,
                errors=[Message(code='read_artifact_error', message=str(e))],
            )
