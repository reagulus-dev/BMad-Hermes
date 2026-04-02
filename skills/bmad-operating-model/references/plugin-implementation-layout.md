# BMad Workflow Plugin: Canonical Implementation Layout

This reference captures the canonical file/module implementation layout for the first BMad workflow plugin pass.

Chosen schema architecture:
- shared common schema modules
- shared artifact/state models
- one schema file per tool

## Canonical implementation layout

```text
alice_workflow_plugin/
  __init__.py
  plugin.py

  registry/
    __init__.py
    loader.py
    models.py
    artifact_contracts.yaml

  schemas/
    __init__.py
    common.py
    artifact_models.py

    bmad_get_state.py
    bmad_get_artifact_contract.py
    bmad_create_artifact_from_template.py
    bmad_validate_artifact.py
    bmad_read_artifact.py
    bmad_update_artifact_section.py
    bmad_sync_story_status.py
    bmad_next_workflow.py

  paths/
    __init__.py
    resolver.py

  parsers/
    __init__.py
    markdown_sections.py
    story_parser.py
    sprint_status_parser.py

  validators/
    __init__.py
    common.py
    story_validator.py
    sprint_status_validator.py

  mutations/
    __init__.py
    template_renderer.py
    checkbox_ops.py
    story_mutator.py
    sprint_status_mutator.py

  state/
    __init__.py
    state_reader.py
    state_normalizer.py
    state_writer.py

  routing/
    __init__.py
    routing_rules.py
    workflow_router.py

  services/
    __init__.py
    artifact_service.py
    state_service.py
    sync_service.py
    workflow_service.py

  tools/
    __init__.py
    bmad_get_state.py
    bmad_get_artifact_contract.py
    bmad_create_artifact_from_template.py
    bmad_validate_artifact.py
    bmad_read_artifact.py
    bmad_update_artifact_section.py
    bmad_sync_story_status.py
    bmad_next_workflow.py

  tests/
    test_registry_loader.py
    test_path_resolver.py
    test_story_parser.py
    test_story_validator.py
    test_story_mutator.py
    test_sprint_status_parser.py
    test_sprint_status_validator.py
    test_sprint_status_mutator.py
    test_state_reader.py
    test_state_normalizer.py
    test_state_writer.py
    test_sync_service.py
    test_workflow_router.py
    test_tool_handlers.py
```

## Canonical module responsibilities

### plugin.py
- plugin entrypoint
- register all 8 tools
- create shared service container
- wire request schema -> service call -> response schema
- no business logic here

### registry/
- source of truth for artifact contracts
- `artifact_contracts.yaml` contains machine-readable contracts
- `models.py` contains typed registry structures
- `loader.py` loads YAML into typed models

### schemas/
The canonical schema architecture.

#### schemas/common.py
Shared enums and shared response components:
- ArtifactType
- WorkflowId
- StateRegime
- TrustLevel
- StoryStatus
- SprintEntryType
- Message
- ErrorMessage
- ValidationResult
- UpdateResult

#### schemas/artifact_models.py
Shared domain models:
- StoryDocument
- SprintStatusEntry
- SprintStatusDocument
- NormalizedState
- RoutingDecision
- ArtifactContractSummary

#### one schema file per tool
- bmad_get_state.py
- bmad_get_artifact_contract.py
- bmad_create_artifact_from_template.py
- bmad_validate_artifact.py
- bmad_read_artifact.py
- bmad_update_artifact_section.py
- bmad_sync_story_status.py
- bmad_next_workflow.py

Each tool schema file contains only that tool's request/response models.

### paths/resolver.py
- resolve canonical and legacy artifact paths
- report ambiguity instead of silently guessing

### parsers/
- `markdown_sections.py`: generic markdown parser
- `story_parser.py`: parse story into StoryDocument
- `sprint_status_parser.py`: parse sprint-status into SprintStatusDocument

### validators/
- `story_validator.py`: validate story contract + transitions
- `sprint_status_validator.py`: validate YAML structure, ordering, statuses, transitions

### mutations/
- `template_renderer.py`: render template-backed artifacts
- `checkbox_ops.py`: safe checkbox operations
- `story_mutator.py`: workflow-aware section-safe story edits
- `sprint_status_mutator.py`: entry-level status updates with transition enforcement

### state/
- `state_reader.py`: read raw `_bmad/state.json`
- `state_normalizer.py`: normalize legacy/modern state into one model
- `state_writer.py`: safe atomic updates to state

### routing/
- `routing_rules.py`: explicit workflow rule table
- `workflow_router.py`: compute next workflow and recommended skill

### services/
- `artifact_service.py`: contract lookup, read, validate, create
- `state_service.py`: normalized state operations
- `sync_service.py`: synchronize story + sprint_status + state.json
- `workflow_service.py`: compute next workflow / recommended skill

### tools/
Thin Hermes tool adapters only.
Each tool:
1. validate request against its schema
2. call one service
3. validate/serialize response against its schema
4. return structured payload

## Canonical dependency flow

- plugin.py -> tools/
- tools/ -> schemas/ and services/
- services/ -> registry/, paths/, parsers/, validators/, mutations/, state/, routing/
- routing/ -> state/, parsers/, registry/
- mutations/ -> registry/ and schemas/artifact_models.py
- validators/ -> registry/ and schemas/artifact_models.py
- parsers/ -> schemas/artifact_models.py
- registry/ should remain as independent as practical

## Canonical first-pass implementation order

### Phase 1: schema and registry foundation
1. schemas/common.py
2. schemas/artifact_models.py
3. schemas/bmad_get_state.py
4. schemas/bmad_get_artifact_contract.py
5. schemas/bmad_create_artifact_from_template.py
6. schemas/bmad_validate_artifact.py
7. schemas/bmad_read_artifact.py
8. schemas/bmad_update_artifact_section.py
9. schemas/bmad_sync_story_status.py
10. schemas/bmad_next_workflow.py
11. registry/models.py
12. registry/loader.py
13. registry/artifact_contracts.yaml

### Phase 2: path + parser foundation
14. paths/resolver.py
15. parsers/markdown_sections.py
16. parsers/story_parser.py
17. parsers/sprint_status_parser.py

### Phase 3: validators
18. validators/common.py
19. validators/story_validator.py
20. validators/sprint_status_validator.py

### Phase 4: mutations
21. mutations/template_renderer.py
22. mutations/checkbox_ops.py
23. mutations/story_mutator.py
24. mutations/sprint_status_mutator.py

### Phase 5: state + routing
25. state/state_reader.py
26. state/state_normalizer.py
27. state/state_writer.py
28. routing/routing_rules.py
29. routing/workflow_router.py

### Phase 6: services
30. services/artifact_service.py
31. services/state_service.py
32. services/sync_service.py
33. services/workflow_service.py

### Phase 7: tools + plugin registration
34. tools/bmad_get_state.py
35. tools/bmad_get_artifact_contract.py
36. tools/bmad_create_artifact_from_template.py
37. tools/bmad_validate_artifact.py
38. tools/bmad_read_artifact.py
39. tools/bmad_update_artifact_section.py
40. tools/bmad_sync_story_status.py
41. tools/bmad_next_workflow.py
42. plugin.py

## Canonical design rules

1. Schemas are split per tool, with shared models centralized.
2. Registry is externalized in YAML, not hardcoded across modules.
3. Artifact mutation must be transactional: parse -> permission check -> apply in memory -> validate -> write.
4. Story files cannot be rewritten wholesale except through create-story initialization.
5. Sprint status transitions must be checked against contract rules before writing.
6. Workflow routing must come from routing/ and services/, not tool wrappers.
7. Legacy path support belongs in paths/resolver.py, not scattered through business logic.

## Why this is canonical

This layout supports:
- explicit artifact contracts
- exact tool schemas
- clean separation of concerns
- future expansion without rewiring
- predictable places to find schemas, contracts, parsers, validators, mutators, routing, and tools
