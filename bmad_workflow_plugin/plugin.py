from __future__ import annotations

from typing import Callable

from bmad_workflow_plugin.registry.loader import RegistryLoader
from bmad_workflow_plugin.services.artifact_service import ArtifactService
from bmad_workflow_plugin.services.init_service import InitService
from bmad_workflow_plugin.services.state_migration_service import StateMigrationService
from bmad_workflow_plugin.services.state_service import StateService
from bmad_workflow_plugin.services.sync_service import SyncService
from bmad_workflow_plugin.services.workflow_service import WorkflowService
from bmad_workflow_plugin.tools.bmad_get_state import BmadGetStateTool
from bmad_workflow_plugin.tools.bmad_init_project import BmadInitProjectTool
from bmad_workflow_plugin.tools.bmad_migrate_state import BmadMigrateStateTool
from bmad_workflow_plugin.tools.bmad_get_artifact_contract import BmadGetArtifactContractTool
from bmad_workflow_plugin.tools.bmad_create_artifact_from_template import BmadCreateArtifactFromTemplateTool
from bmad_workflow_plugin.tools.bmad_validate_artifact import BmadValidateArtifactTool
from bmad_workflow_plugin.tools.bmad_read_artifact import BmadReadArtifactTool
from bmad_workflow_plugin.tools.bmad_update_artifact_section import BmadUpdateArtifactSectionTool
from bmad_workflow_plugin.tools.bmad_sync_story_status import BmadSyncStoryStatusTool
from bmad_workflow_plugin.tools.bmad_next_workflow import BmadNextWorkflowTool
from bmad_workflow_plugin.tools.bmad_workflow_help import BmadWorkflowHelpTool


class BmadWorkflowPlugin:
    """Plugin entrypoint and service container."""

    def __init__(self) -> None:
        self._registry = None
        self._artifact_service = None
        self._init_service = None
        self._state_migration_service = None
        self._state_service = None
        self._sync_service = None
        self._workflow_service = None
        self._tools: dict[str, object] = {}
        self._tool_factories: dict[str, Callable[[], object]] = {
            'bmad_get_state': lambda: BmadGetStateTool(self.state_service),
            'bmad_init_project': lambda: BmadInitProjectTool(self.init_service),
            'bmad_migrate_state': lambda: BmadMigrateStateTool(self.state_migration_service),
            'bmad_get_artifact_contract': lambda: BmadGetArtifactContractTool(self.artifact_service),
            'bmad_create_artifact_from_template': lambda: BmadCreateArtifactFromTemplateTool(self.artifact_service),
            'bmad_validate_artifact': lambda: BmadValidateArtifactTool(self.artifact_service),
            'bmad_read_artifact': lambda: BmadReadArtifactTool(self.artifact_service),
            'bmad_update_artifact_section': lambda: BmadUpdateArtifactSectionTool(self.artifact_service),
            'bmad_sync_story_status': lambda: BmadSyncStoryStatusTool(self.sync_service),
            'bmad_next_workflow': lambda: BmadNextWorkflowTool(self.workflow_service),
            'bmad_workflow_help': lambda: BmadWorkflowHelpTool(self.workflow_service),
        }

    @property
    def registry(self):
        if self._registry is None:
            self._registry = RegistryLoader().load_default()
        return self._registry

    @property
    def artifact_service(self) -> ArtifactService:
        if self._artifact_service is None:
            self._artifact_service = ArtifactService(registry=self.registry)
        return self._artifact_service

    @property
    def init_service(self) -> InitService:
        if self._init_service is None:
            self._init_service = InitService()
        return self._init_service

    @property
    def state_migration_service(self) -> StateMigrationService:
        if self._state_migration_service is None:
            self._state_migration_service = StateMigrationService(registry=self.registry)
        return self._state_migration_service

    @property
    def state_service(self) -> StateService:
        if self._state_service is None:
            self._state_service = StateService(registry=self.registry)
        return self._state_service

    @property
    def sync_service(self) -> SyncService:
        if self._sync_service is None:
            self._sync_service = SyncService(
                registry=self.registry,
                artifact_service=self.artifact_service,
                state_service=self.state_service,
            )
        return self._sync_service

    @property
    def workflow_service(self) -> WorkflowService:
        if self._workflow_service is None:
            self._workflow_service = WorkflowService()
        return self._workflow_service

    def get_tool(self, name: str) -> object:
        tool = self._tools.get(name)
        if tool is not None:
            return tool
        factory = self._tool_factories.get(name)
        if factory is None:
            raise KeyError(f'Unknown tool: {name}')
        tool = factory()
        self._tools[name] = tool
        return tool

    def build_tools(self) -> dict[str, object]:
        return {name: self.get_tool(name) for name in self._tool_factories}


def register_plugin(api) -> BmadWorkflowPlugin:
    """Return plugin instance; caller can register handlers from `build_tools()`."""
    plugin = BmadWorkflowPlugin()
    return plugin
