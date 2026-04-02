from __future__ import annotations

ROUTING_RULES = [
    {'state_regime': 'missing', 'next_workflow_id': 'project-init', 'recommended_skill': 'bmad-project-init'},
    {'state_regime': 'legacy_only', 'next_workflow_id': 'state-migration', 'recommended_skill': 'bmad-state-migration'},
    {'state_regime': 'partially_normalized', 'next_workflow_id': 'state-check', 'recommended_skill': 'bmad-state-check'},
]
