from __future__ import annotations

from pathlib import Path

import pytest

from bmad_workflow_plugin.services.artifact_service import ArtifactService


ARTIFACT_CASES = [
    (
        'brainstorming_session',
        {
            'session_name': 'auth-brainstorm',
            'date': '2026-04-02',
            'user_name': 'reagulus',
            'session_goal': 'Explore authentication ideas',
            'techniques': 'mindmap',
            'agent_model_name_version': 'test-agent',
            'session_output_path': '/tmp/auth-brainstorm.md',
        },
        'auth-brainstorm',
        'bmad-brainstorming',
        'ideas',
        'Capture SSO and passkey options.',
    ),
    (
        'product_brief',
        {
            'project_name': 'acme-app',
            'status': 'draft',
            'agent_model_name_version': 'test-agent',
            'artifact_path': '/tmp/brief.md',
        },
        'acme-app',
        'bmad-product-brief',
        'executive_summary',
        'Acme App eliminates manual triage for small teams.',
    ),
    (
        'prfaq',
        {
            'project_name': 'acme-app',
            'status': 'draft',
            'headline': 'Acme App launches instant team triage',
            'subheadline': 'Small teams resolve urgent requests faster.',
            'city': 'Austin, TX',
            'date': '2026-04-02',
            'opening_paragraph': 'Today Acme announced a faster way to handle incoming work.',
            'problem_paragraph': 'Teams lose time switching between fragmented queues.',
            'solution_paragraph': 'Acme App centralizes and prioritizes urgent work in one place.',
            'hardest_customer_question': 'Will this replace our helpdesk?',
            'hardest_internal_question': 'How do we price adoption?',
            'next_question': 'What does onboarding look like?',
            'answer': 'Customers connect existing systems and see priority queues immediately.',
            'agent_model_name_version': 'test-agent',
            'artifact_path': '/tmp/prfaq.md',
        },
        'acme-app',
        'bmad-prfaq',
        'verdict',
        'The concept is strong but needs pricing validation.',
    ),
    (
        'prd',
        {
            'project_name': 'acme-app',
            'status': 'draft',
            'user_name': 'reagulus',
            'date': '2026-04-02',
            'user_type': 'team lead',
            'capability': 'prioritize urgent work',
            'value_benefit': 'my team focuses on the right issues first',
            'precondition': 'incoming requests exist',
            'action': 'I open the dashboard',
            'expected_outcome': 'urgent requests appear at the top',
            'agent_model_name_version': 'test-agent',
            'artifact_path': '/tmp/prd.md',
        },
        'acme-app',
        'bmad-create-prd',
        'overview',
        'Acme App helps operations teams triage requests with confidence.',
    ),
    (
        'prd_validation_report',
        {
            'project_name': 'acme-app',
            'status': 'in_progress',
            'validation_type': 'full',
            'date': '2026-04-02',
            'agent_model_name_version': 'test-agent',
            'artifact_path': '/tmp/prd-validation.md',
        },
        'acme-app',
        'bmad-validate-prd',
        'validation_summary',
        'The PRD is mostly complete and needs measurable success metrics.',
    ),
    (
        'ux_design',
        {
            'project_name': 'acme-app',
            'status': 'draft',
            'user_name': 'reagulus',
            'date': '2026-04-02',
            'agent_model_name_version': 'test-agent',
            'artifact_path': '/tmp/ux-design.md',
        },
        'acme-app',
        'bmad-create-ux-design',
        'core_experience',
        'Users should feel immediate clarity when urgent work arrives.',
    ),
    (
        'architecture',
        {
            'project_name': 'acme-app',
            'status': 'draft',
            'user_name': 'reagulus',
            'date': '2026-04-02',
            'agent_model_name_version': 'test-agent',
            'artifact_path': '/tmp/architecture.md',
        },
        'acme-app',
        'bmad-create-architecture',
        'context',
        'The system must aggregate events from multiple inbound systems.',
    ),
    (
        'epics_and_stories',
        {
            'project_name': 'acme-app',
            'status': 'draft',
            'date': '2026-04-02',
            'epic_goal': 'Deliver an actionable triage workflow',
            'user_type': 'team lead',
            'capability': 'review prioritized work',
            'value_benefit': 'the team responds faster',
            'precondition': 'the queue contains requests',
            'action': 'the lead opens the sprint view',
            'expected_outcome': 'critical work is identified clearly',
            'agent_model_name_version': 'test-agent',
            'artifact_path': '/tmp/epics.md',
        },
        'acme-app',
        'bmad-create-epics-and-stories',
        'overview',
        'This plan decomposes PRD requirements into implementation slices.',
    ),
    (
        'project_context',
        {
            'project_name': 'acme-app',
            'agent_model_name_version': 'test-agent',
            'artifact_path': '/tmp/project-context.md',
        },
        'acme-app',
        'bmad-generate-project-context',
        'critical_rules',
        'Always preserve audit history and favor append-only evidence.',
    ),
]


@pytest.mark.parametrize(
    'artifact_type,template_vars,expected_name,workflow_id,section_id,new_content',
    ARTIFACT_CASES,
)
def test_phase123_artifact_service_create_read_validate_update_round_trip(
    tmp_path: Path,
    artifact_type: str,
    template_vars: dict,
    expected_name: str,
    workflow_id: str,
    section_id: str,
    new_content: str,
) -> None:
    service = ArtifactService()

    create_result = service.create_from_template(
        project_root=str(tmp_path),
        artifact_type=artifact_type,
        template_vars=template_vars,
    )
    created_path = Path(create_result['path'])

    assert created_path.exists()
    assert create_result['artifact_type'] == artifact_type
    assert create_result['validation_result'] is not None
    assert create_result['validation_result'].valid is True

    read_result = service.read_artifact(str(tmp_path), artifact_type, str(created_path))
    doc = read_result['doc']
    assert doc.path == str(created_path.resolve())

    if hasattr(doc, 'project_name'):
        assert doc.project_name == expected_name
    if hasattr(doc, 'session_name'):
        assert doc.session_name in {expected_name, created_path.stem}

    validate_result = service.validate_artifact(str(tmp_path), artifact_type, str(created_path))
    assert validate_result['valid'] is True
    assert validate_result['artifact_path'] == str(created_path.resolve())

    update_result = service.update_artifact_sections(
        project_root=str(tmp_path),
        artifact_type=artifact_type,
        artifact_path=str(created_path),
        workflow_id=workflow_id,
        operations=[
            {
                'type': 'replace_section',
                'section_id': section_id,
                'new_content': new_content,
            }
        ],
    )

    assert update_result['updated'] is True
    assert update_result['validation_result'].valid is True

    read_after = service.read_artifact(str(tmp_path), artifact_type, str(created_path))
    assert read_after['doc'].sections[section_id].strip() == new_content


def test_phase123_service_prefers_contract_paths_for_multiple_artifacts(tmp_path: Path) -> None:
    service = ArtifactService()

    brief = service.create_from_template(
        project_root=str(tmp_path),
        artifact_type='product_brief',
        template_vars={
            'project_name': 'contract-path-app',
            'agent_model_name_version': 'test-agent',
            'artifact_path': '/tmp/brief.md',
        },
    )
    architecture = service.create_from_template(
        project_root=str(tmp_path),
        artifact_type='architecture',
        template_vars={
            'project_name': 'contract-path-app',
            'user_name': 'reagulus',
            'date': '2026-04-02',
            'agent_model_name_version': 'test-agent',
            'artifact_path': '/tmp/architecture.md',
        },
    )

    assert brief['path'].endswith('/_bmad/artifacts/planning/briefs/contract-path-app/brief.md')
    assert architecture['path'].endswith('/_bmad/artifacts/solutioning/architecture/contract-path-app/architecture.md')
