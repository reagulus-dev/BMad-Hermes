from __future__ import annotations

from bmad_workflow_plugin.services.workflow_service import WorkflowService
from bmad_workflow_plugin.tools.bmad_workflow_help import BmadWorkflowHelpTool


class DummyWorkflow:
    workflow_id = 'bmad-project-init'
    display_name = 'Project Init'
    phase = '4-implementation'
    status_triggers = []
    recommended_skill = 'bmad-project-init'
    required = False
    description = 'Initialize project _bmad/ structure and state.json.'
    outputs = ['_bmad/state.json']
    after = []
    before = ['bmad-sprint-planning']
    aliases = ['project-init']


class DummyDecision:
    def __init__(self, target_story_key: str | None = None):
        self.next_workflow_id = 'bmad-project-init'
        self.recommended_skill = 'bmad-project-init'
        self.reason = 'No _bmad/state.json found.'
        self.blocked = False
        self.blockers = []
        self.target_story_key = target_story_key
        self.phase = None


class DummyRouter:
    def next_workflow(self, project_root: str, target_story_key: str | None = None):
        return DummyDecision(target_story_key)

    def get_workflow(self, workflow_id: str):
        if workflow_id == 'project-init':
            return DummyWorkflow()
        return None

    def list_workflows_by_phase(self, phase: str):
        return [DummyWorkflow()]

    def all_workflows(self):
        return [DummyWorkflow()]


class DummyWorkflowService:
    def __init__(self):
        self.calls = []

    def get_workflow(self, workflow_id: str):
        self.calls.append(('get_workflow', workflow_id))
        if workflow_id != 'project-init':
            return None
        return {
            'workflow_id': 'bmad-project-init',
            'display_name': 'Project Init',
            'phase': '4-implementation',
            'status_triggers': [],
            'recommended_skill': 'bmad-project-init',
            'required': False,
            'description': 'Initialize project _bmad/ structure and state.json.',
            'outputs': ['_bmad/state.json'],
            'after': [],
            'before': ['bmad-sprint-planning'],
            'aliases': ['project-init'],
        }

    def list_workflows(self, phase: str | None = None):
        self.calls.append(('list_workflows', phase))
        return [self.get_workflow('project-init')]


def test_workflow_service_lazy_loads_router() -> None:
    counts = {'router': 0}

    def build_router():
        counts['router'] += 1
        return DummyRouter()

    service = WorkflowService(router_factory=build_router)

    assert counts == {'router': 0}

    workflow = service.get_workflow('project-init')

    assert workflow['workflow_id'] == 'bmad-project-init'
    assert counts == {'router': 1}

    workflows = service.list_workflows()

    assert len(workflows) == 1
    assert counts == {'router': 1}


def test_bmad_workflow_help_tool_reuses_workflow_service_without_constructing_router_itself() -> None:
    workflow_service = DummyWorkflowService()
    tool = BmadWorkflowHelpTool(workflow_service)

    response = tool.execute({'workflow_id': 'project-init'})

    assert response.success is True
    assert response.data.workflow_id == 'bmad-project-init'
    assert workflow_service.calls == [('get_workflow', 'project-init')]
