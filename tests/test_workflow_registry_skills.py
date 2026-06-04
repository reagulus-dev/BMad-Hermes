from pathlib import Path

from bmad_workflow_plugin.registry.workflow_loader import WorkflowRegistryLoader


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / 'skills'


def test_every_registered_workflow_points_to_bundled_skill() -> None:
    registry = WorkflowRegistryLoader().load()

    missing = sorted(
        {
            workflow.recommended_skill
            for workflow in registry.workflows.values()
            if workflow.recommended_skill
            and not (SKILLS_DIR / workflow.recommended_skill / 'SKILL.md').exists()
        }
    )

    assert missing == []


def test_every_bundled_bmad_skill_is_registered_or_intentionally_doctrine_only() -> None:
    registry = WorkflowRegistryLoader().load()
    registered_skills = {
        workflow.recommended_skill
        for workflow in registry.workflows.values()
        if workflow.recommended_skill
    }
    bundled_skills = {path.parent.name for path in SKILLS_DIR.glob('bmad-*/SKILL.md')}
    doctrine_only = {
        'bmad-artifact-policy',
        'bmad-evidence-reporting',
        'bmad-operating-model',
    }

    assert sorted(bundled_skills - registered_skills - doctrine_only) == []
