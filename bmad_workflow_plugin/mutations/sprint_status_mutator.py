from __future__ import annotations

import yaml

from bmad_workflow_plugin.schemas.artifact_models import SprintStatusDocument, SprintStatusEntry


class SprintStatusMutator:
    """Entry-level sprint status updates with transition enforcement delegated to the validator."""

    def set_entry_status(
        self, doc: SprintStatusDocument, key: str, new_status: str, workflow_id: str, contract
    ) -> SprintStatusDocument:
        """
        Set the status of a single development_status entry by key.
        Returns a new SprintStatusDocument with the updated entry and re-serialized raw_text.
        Raises KeyError if key is not found.
        Validation of the transition itself is the caller's responsibility (use SprintStatusValidator).
        """
        # Find and update entry
        new_entries: list[SprintStatusEntry] = []
        found = False
        for entry in doc.development_status:
            if entry.key == key:
                new_entries.append(SprintStatusEntry(
                    key=entry.key,
                    entry_type=entry.entry_type,
                    status=new_status,
                ))
                found = True
            else:
                new_entries.append(entry)

        if not found:
            raise KeyError(f'Entry key not found in sprint status: {key!r}')

        # Reconstruct YAML raw_text preserving original structure as much as possible
        new_raw = self._rebuild_yaml(doc, new_entries)

        return SprintStatusDocument(
            path=doc.path,
            metadata=dict(doc.metadata),
            development_status=new_entries,
            raw_text=new_raw,
        )

    def _rebuild_yaml(self, doc: SprintStatusDocument, entries: list[SprintStatusEntry]) -> str:
        """Re-serialize the sprint status document to YAML string."""
        # Group entries by type for ordered output
        epics = [e for e in entries if e.entry_type == 'epic']
        retros = [e for e in entries if e.entry_type == 'retrospective']
        stories = [e for e in entries if e.entry_type == 'story']

        # Build ordered development_status dict (epic, retro, then stories)
        dev_status: dict[str, str] = {}
        for e in epics:
            dev_status[e.key] = e.status
        for e in retros:
            dev_status[e.key] = e.status
        for e in stories:
            dev_status[e.key] = e.status

        payload = {
            'generated': doc.metadata.get('generated'),
            'project': doc.metadata.get('project'),
            'project_key': doc.metadata.get('project_key'),
            'tracking_system': doc.metadata.get('tracking_system'),
            'story_location': doc.metadata.get('story_location'),
            'development_status': dev_status,
        }
        return yaml.dump(payload, default_flow_style=False, sort_keys=False, allow_unicode=True)
