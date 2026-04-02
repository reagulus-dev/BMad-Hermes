from __future__ import annotations

from bmad_workflow_plugin.schemas.bmad_update_artifact_section import (
    BmadUpdateArtifactSectionRequest,
    BmadUpdateArtifactSectionResponse,
    BmadBmadUpdateArtifactSectionResponseData,
)
from bmad_workflow_plugin.schemas.common import Message


class BmadUpdateArtifactSectionTool:
    def __init__(self, artifact_service) -> None:
        self.artifact_service = artifact_service

    def execute(self, request: BmadUpdateArtifactSectionRequest | dict) -> BmadUpdateArtifactSectionResponse:
        if isinstance(request, dict):
            request = BmadUpdateArtifactSectionRequest(**request)
        try:
            # Normalize schema operation objects to plain dicts for the service
            operations = self._normalize_ops(request.operations)
            result = self.artifact_service.update_artifact_sections(
                project_root=request.project_root,
                artifact_type=request.artifact_type.value,
                artifact_path=request.artifact_path,
                workflow_id=request.workflow_id.value,
                operations=operations,
            )
            return BmadUpdateArtifactSectionResponse(
                success=True,
                data=BmadBmadUpdateArtifactSectionResponseData(
                    artifact_type=request.artifact_type.value,
                    artifact_path=request.artifact_path,
                    applied_operations=len(operations),
                    validation=result['validation_result'],
                    updated_summary={
                        'story_key': result['notes'][0].split()[-1] if result['notes'] else '',
                    },
                ),
            )
        except Exception as e:
            return BmadUpdateArtifactSectionResponse(
                success=False,
                data=None,
                errors=[Message(code='update_section_error', message=str(e))],
            )

    def _normalize_ops(self, operations: list[object]) -> list[dict]:
        """Convert schema dataclass operation objects to plain service-compatible dicts."""
        out = []
        for op in operations:
            if hasattr(op, '__dict__'):
                d = vars(op).copy()
                # Rename schema → service field names
                d['type'] = d.pop('op', None)          # op → type
                d['section_id'] = d.pop('section', None)  # section → section_id
                d['new_content'] = d.pop('content', None) # content → new_content (AppendSectionOp, ReplaceSectionOp)
                out.append(d)
            elif isinstance(op, dict):
                d = dict(op)
                d.setdefault('type', d.pop('op', None))
                d.setdefault('section_id', d.pop('section', None))
                d.setdefault('new_content', d.pop('content', None))
                out.append(d)
            else:
                raise ValueError(f'Unknown operation type: {type(op)}')
        return out
