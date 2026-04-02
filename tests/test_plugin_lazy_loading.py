from __future__ import annotations

from bmad_workflow_plugin.plugin import BmadWorkflowPlugin


def test_plugin_container_lazy_creates_services_and_caches_tools() -> None:
    plugin = BmadWorkflowPlugin()

    assert plugin._registry is None
    assert plugin._artifact_service is None
    assert plugin._init_service is None
    assert plugin._state_migration_service is None
    assert plugin._state_service is None
    assert plugin._sync_service is None
    assert plugin._workflow_service is None
    assert plugin._tools == {}

    get_state_tool = plugin.get_tool('bmad_get_state')

    assert plugin._registry is not None
    assert plugin._state_service is not None
    assert plugin._artifact_service is None
    assert plugin._init_service is None
    assert plugin._state_migration_service is None
    assert plugin._sync_service is None
    assert plugin._workflow_service is None
    assert plugin._tools['bmad_get_state'] is get_state_tool

    same_get_state_tool = plugin.get_tool('bmad_get_state')
    assert same_get_state_tool is get_state_tool

    workflow_help_tool = plugin.get_tool('bmad_workflow_help')

    assert plugin._workflow_service is not None
    assert plugin._tools['bmad_workflow_help'] is workflow_help_tool
    assert plugin._artifact_service is None
    assert plugin._state_migration_service is None
    assert plugin._sync_service is None

    tools = plugin.build_tools()
    assert len(tools) >= 11
    assert tools['bmad_get_state'] is get_state_tool
    assert tools['bmad_workflow_help'] is workflow_help_tool
