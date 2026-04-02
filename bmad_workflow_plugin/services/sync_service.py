from __future__ import annotations

from pathlib import Path

from bmad_workflow_plugin.parsers.sprint_status_parser import SprintStatusParser
from bmad_workflow_plugin.validators.sprint_status_validator import SprintStatusValidator
from bmad_workflow_plugin.mutations.sprint_status_mutator import SprintStatusMutator


class SyncService:
    def __init__(self, registry, artifact_service, state_service) -> None:
        self.registry = registry
        self.artifact_service = artifact_service
        self.state_service = state_service
        self._sprint_parser = SprintStatusParser()
        self._sprint_validator = SprintStatusValidator()
        self._sprint_mutator = SprintStatusMutator()

    def sync_story_status(
        self, project_root: str, story_key: str, new_status: str,
        source_workflow: str, reason: str | None = None
    ) -> dict:
        """
        Update a story's status in sprint_status.yaml and propagate to state.json.

        Transaction: read sprint_status -> validate transition -> mutate -> write ->
        patch state.json current_story / workflow_status.
        """
        # Resolve sprint_status path
        sprint_result = self.artifact_service.read_artifact(
            project_root, 'sprint_status', artifact_path=None
        )
        sprint_doc = sprint_result['doc']
        contract = sprint_result['contract']

        # Capture previous doc for transition validation
        previous_doc = sprint_doc

        # Mutate: set the entry status
        updated_doc = self._sprint_mutator.set_entry_status(
            sprint_doc, story_key, new_status, source_workflow, contract
        )

        # Validate the transition
        validation = self._sprint_validator.validate(updated_doc, contract, previous_doc=previous_doc)
        if not validation.valid:
            errors = [f'{e.code}: {e.message}' for e in validation.errors]
            raise ValueError(f'Sprint status transition is invalid: {errors}')

        # Write updated sprint_status
        Path(updated_doc.path).write_text(updated_doc.raw_text, encoding='utf-8')

        # Patch state.json
        patch = {
            'current_story': story_key,
            'workflow_status': source_workflow,
        }
        state_path = self.state_service.patch_state(project_root, patch)

        return {
            'story_key': story_key,
            'previous_status': next(
                (e.status for e in previous_doc.development_status if e.key == story_key), None
            ),
            'new_status': new_status,
            'sprint_status_path': updated_doc.path,
            'state_path': state_path,
            'source_workflow': source_workflow,
            'validation_result': validation,
            'notes': [reason] if reason else [],
        }
