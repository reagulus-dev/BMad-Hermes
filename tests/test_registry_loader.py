from bmad_workflow_plugin.registry.loader import RegistryLoader


def test_registry_loader_loads_default() -> None:
    registry = RegistryLoader().load_default()
    assert 'story' in registry
    assert 'sprint_status' in registry
