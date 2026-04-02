# BMad Workflow Plugin: Starter Skeleton

This reference provides a concrete starter skeleton for the first plugin pass.
It is intentionally a scaffold of exact module/class/function names and signatures so implementation can start cleanly without rediscovering architecture.

## Why starter skeleton rather than full implementation immediately

A starter skeleton is the correct next deliverable because it:
- locks in the canonical architecture
- gives exact file/class/function names
- keeps implementation modular and reviewable
- avoids prematurely filling complex logic before contract details settle
- minimizes later rewiring because interfaces are defined early

This is not "only stubs" in the dismissive sense.
It is an interface-first build plan.

## Suggested package skeleton

```python
# alice_workflow_plugin/plugin.py
from alice_workflow_plugin.registry.loader import RegistryLoader
from alice_workflow_plugin.services.artifact_service import ArtifactService
from alice_workflow_plugin.services.state_service import StateService
from alice_workflow_plugin.services.sync_service import SyncService
from alice_workflow_plugin.services.workflow_service import WorkflowService


def register_plugin(api) -> None:
    registry = RegistryLoader().load_default()

    artifact_service = ArtifactService(registry=registry)
    state_service = StateService(registry=registry)
    sync_service = SyncService(registry=registry, artifact_service=artifact_service, state_service=state_service)
    workflow_service = WorkflowService(registry=registry, artifact_service=artifact_service, state_service=state_service)

    # register Hermes tools here
```

## Registry layer

```python
# registry/models.py
from dataclasses import dataclass
from typing import Any

@dataclass
class ArtifactContract:
    artifact_type: str
    contract_version: str
    display_name: str
    phase: str
    format: str
    raw: dict[str, Any]
```

```python
# registry/loader.py
from pathlib import Path
from .models import ArtifactContract

class RegistryLoader:
    def __init__(self, registry_path: str | None = None) -> None:
        self.registry_path = registry_path

    def load_default(self) -> dict[str, ArtifactContract]:
        raise NotImplementedError

    def get_contract(self, artifact_type: str) -> ArtifactContract:
        raise NotImplementedError
```

## Schema layer

```python
# schemas/common.py
from pydantic import BaseModel
from typing import Any

class Message(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = {}

class ValidationResult(BaseModel):
    valid: bool
    errors: list[Message] = []
    warnings: list[Message] = []
    parsed_summary: dict[str, Any] | None = None

class UpdateResult(BaseModel):
    updated: bool
    path: str | None
    notes: list[str] = []
```

```python
# schemas/artifact_models.py
from pydantic import BaseModel
from typing import Any

class StoryDocument(BaseModel):
    path: str
    story_key: str
    title: str
    status: str
    sections: dict[str, str]
    raw_text: str

class SprintStatusEntry(BaseModel):
    key: str
    entry_type: str
    status: str

class SprintStatusDocument(BaseModel):
    path: str
    metadata: dict[str, Any]
    development_status: list[SprintStatusEntry]
    raw_text: str

class NormalizedState(BaseModel):
    project_root: str
    state_regime: str
    trust_level: str
    normalized_state: dict[str, Any]

class RoutingDecision(BaseModel):
    next_workflow_id: str
    recommended_skill: str
    reason: str
    blocked: bool
    blockers: list[str]
    target_story_key: str | None = None
```

Each per-tool schema file should define Request/Response models only.

## Path resolution

```python
# paths/resolver.py
from dataclasses import dataclass

@dataclass
class ResolvedPath:
    path: str | None
    source_kind: str | None  # preferred | legacy | none
    candidates: list[str]
    ambiguous: bool

class PathResolver:
    def resolve_artifact_path(self, project_root: str, artifact_type: str, identity: dict) -> ResolvedPath:
        raise NotImplementedError

    def build_preferred_path(self, project_root: str, artifact_type: str, identity: dict) -> str:
        raise NotImplementedError
```

## Parser layer

```python
# parsers/markdown_sections.py
class MarkdownSectionsParser:
    def parse(self, text: str) -> dict:
        raise NotImplementedError
```

```python
# parsers/story_parser.py
from alice_workflow_plugin.schemas.artifact_models import StoryDocument

class StoryParser:
    def parse(self, path: str, text: str) -> StoryDocument:
        raise NotImplementedError
```

```python
# parsers/sprint_status_parser.py
from alice_workflow_plugin.schemas.artifact_models import SprintStatusDocument

class SprintStatusParser:
    def parse(self, path: str, text: str) -> SprintStatusDocument:
        raise NotImplementedError
```

## Validator layer

```python
# validators/story_validator.py
from alice_workflow_plugin.schemas.common import ValidationResult
from alice_workflow_plugin.schemas.artifact_models import StoryDocument
from alice_workflow_plugin.registry.models import ArtifactContract

class StoryValidator:
    def validate(self, doc: StoryDocument, contract: ArtifactContract, previous_status: str | None = None) -> ValidationResult:
        raise NotImplementedError
```

```python
# validators/sprint_status_validator.py
from alice_workflow_plugin.schemas.common import ValidationResult
from alice_workflow_plugin.schemas.artifact_models import SprintStatusDocument
from alice_workflow_plugin.registry.models import ArtifactContract

class SprintStatusValidator:
    def validate(self, doc: SprintStatusDocument, contract: ArtifactContract, previous_doc: SprintStatusDocument | None = None) -> ValidationResult:
        raise NotImplementedError
```

## Mutation layer

```python
# mutations/template_renderer.py
class TemplateRenderer:
    def render(self, template_path: str, template_vars: dict) -> str:
        raise NotImplementedError
```

```python
# mutations/checkbox_ops.py
class CheckboxOps:
    def set_checkbox(self, section_text: str, match_text: str, checked: bool) -> str:
        raise NotImplementedError
```

```python
# mutations/story_mutator.py
from alice_workflow_plugin.schemas.artifact_models import StoryDocument

class StoryMutator:
    def apply_operations(self, doc: StoryDocument, workflow_id: str, operations: list[dict], contract) -> StoryDocument:
        raise NotImplementedError
```

```python
# mutations/sprint_status_mutator.py
from alice_workflow_plugin.schemas.artifact_models import SprintStatusDocument

class SprintStatusMutator:
    def set_entry_status(self, doc: SprintStatusDocument, key: str, new_status: str, workflow_id: str, contract) -> SprintStatusDocument:
        raise NotImplementedError
```

## State layer

```python
# state/state_reader.py
class StateReader:
    def read(self, project_root: str) -> dict | None:
        raise NotImplementedError
```

```python
# state/state_normalizer.py
from alice_workflow_plugin.schemas.artifact_models import NormalizedState

class StateNormalizer:
    def normalize(self, project_root: str, raw_state: dict | None) -> NormalizedState:
        raise NotImplementedError
```

```python
# state/state_writer.py
class StateWriter:
    def write_patch(self, project_root: str, patch: dict) -> str:
        raise NotImplementedError
```

## Routing layer

```python
# routing/routing_rules.py
ROUTING_RULES = [
    # encode first-pass explicit workflow routing here
]
```

```python
# routing/workflow_router.py
from alice_workflow_plugin.schemas.artifact_models import RoutingDecision

class WorkflowRouter:
    def next_workflow(self, project_root: str, target_story_key: str | None = None) -> RoutingDecision:
        raise NotImplementedError
```

## Service layer

```python
# services/artifact_service.py
class ArtifactService:
    def __init__(self, registry) -> None:
        self.registry = registry

    def get_contract(self, artifact_type: str):
        raise NotImplementedError

    def read_artifact(self, project_root: str, artifact_type: str, artifact_path: str | None = None):
        raise NotImplementedError

    def validate_artifact(self, project_root: str, artifact_type: str, artifact_path: str | None = None):
        raise NotImplementedError

    def create_from_template(self, project_root: str, artifact_type: str, template_vars: dict, inventory: dict | None = None, destination_path: str | None = None, overwrite: bool = False):
        raise NotImplementedError

    def update_story_sections(self, project_root: str, artifact_path: str, workflow_id: str, operations: list[dict]):
        raise NotImplementedError
```

```python
# services/state_service.py
class StateService:
    def __init__(self, registry) -> None:
        self.registry = registry

    def get_state(self, project_root: str):
        raise NotImplementedError

    def patch_state(self, project_root: str, patch: dict):
        raise NotImplementedError
```

```python
# services/sync_service.py
class SyncService:
    def __init__(self, registry, artifact_service, state_service) -> None:
        self.registry = registry
        self.artifact_service = artifact_service
        self.state_service = state_service

    def sync_story_status(self, project_root: str, story_key: str, new_status: str, source_workflow: str, reason: str | None = None):
        raise NotImplementedError
```

```python
# services/workflow_service.py
class WorkflowService:
    def __init__(self, registry, artifact_service, state_service) -> None:
        self.registry = registry
        self.artifact_service = artifact_service
        self.state_service = state_service

    def next_workflow(self, project_root: str, target_story_key: str | None = None):
        raise NotImplementedError
```

## Tool handlers

Each tool handler should be thin.

Example:

```python
# tools/bmad_get_state.py
class BmadGetStateTool:
    def __init__(self, state_service) -> None:
        self.state_service = state_service

    def execute(self, request):
        return self.state_service.get_state(request.project_root)
```

Repeat similarly for:
- bmad_get_artifact_contract
- bmad_create_artifact_from_template
- bmad_validate_artifact
- bmad_read_artifact
- bmad_update_artifact_section
- bmad_sync_story_status
- bmad_next_workflow

## Testing starter plan

At minimum, implement tests in this order:
1. registry loading
2. story parsing
3. story validation
4. story mutation permissions
5. sprint-status parsing
6. sprint-status transition validation
7. state normalization
8. workflow routing
9. tool handler I/O validation

## Notes

The skeleton should be filled in incrementally in the canonical implementation order documented in `references/plugin-implementation-layout.md`.

The point of this skeleton is not to defer real work indefinitely.
It is to freeze architecture and interface boundaries before implementation logic expands.
That reduces later rewiring and keeps the plugin auditable.
