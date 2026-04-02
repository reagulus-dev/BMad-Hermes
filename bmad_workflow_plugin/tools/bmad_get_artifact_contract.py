from __future__ import annotations

from bmad_workflow_plugin.schemas.bmad_get_artifact_contract import (
    BmadGetArtifactContractRequest,
    BmadGetArtifactContractResponse,
    BmadBmadGetArtifactContractResponseData,
)
from bmad_workflow_plugin.schemas.artifact_models import ArtifactContractSummary
from bmad_workflow_plugin.schemas.common import Message


class BmadGetArtifactContractTool:
    def __init__(self, artifact_service) -> None:
        self.artifact_service = artifact_service

    def execute(self, request: BmadGetArtifactContractRequest | dict) -> BmadGetArtifactContractResponse:
        if isinstance(request, dict):
            request = BmadGetArtifactContractRequest(**request)
        try:
            contract = self.artifact_service.get_contract(request.artifact_type.value)
            summary = ArtifactContractSummary(
                artifact_type=contract.artifact_type,
                contract_version=contract.contract_version,
                display_name=contract.display_name,
                phase=contract.phase,
                format=contract.format,
                details={},
            )
            return BmadGetArtifactContractResponse(success=True, data=summary)
        except Exception as e:
            return BmadGetArtifactContractResponse(
                success=False,
                data=None,
                errors=[Message(code='contract_lookup_error', message=str(e))],
            )
