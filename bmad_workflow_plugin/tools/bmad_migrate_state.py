from __future__ import annotations

from bmad_workflow_plugin.schemas.bmad_migrate_state import (
    BmadMigrateStateRequest,
    BmadMigrateStateResponse,
    BmadMigrateStateResponseData,
)
from bmad_workflow_plugin.schemas.common import Message


class BmadMigrateStateTool:
    def __init__(self, migration_service) -> None:
        self.migration_service = migration_service

    def execute(self, request: BmadMigrateStateRequest | dict) -> BmadMigrateStateResponse:
        if isinstance(request, dict):
            request = BmadMigrateStateRequest(**request)
        try:
            result = self.migration_service.migrate(request.project_root)
            return BmadMigrateStateResponse(
                success=True,
                data=BmadMigrateStateResponseData(**result),
            )
        except Exception as e:
            return BmadMigrateStateResponse(
                success=False,
                data=None,
                errors=[Message(code='state_migration_error', message=str(e))],
            )