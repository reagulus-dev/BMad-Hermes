from bmad_workflow_plugin.state.state_normalizer import StateNormalizer


def test_state_normalizer_detects_missing() -> None:
    state = StateNormalizer().normalize('/tmp/demo', None)
    assert state.state_regime == 'missing'


def test_state_normalizer_detects_legacy_only() -> None:
    raw = {'projectName': 'demo', 'currentPhase': 'implementation', 'completedWorkflows': []}
    state = StateNormalizer().normalize('/tmp/demo', raw)
    assert state.state_regime == 'legacy_only'
