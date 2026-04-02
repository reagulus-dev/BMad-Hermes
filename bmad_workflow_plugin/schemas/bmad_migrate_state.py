from __future__ import annotations

from dataclasses import dataclass, field

from bmad_workflow_plugin.schemas.common import Message


@dataclass(slots=True)
class BmadMigrateStateRequest:
    project_root: str


@dataclass(slots=True)
class BmadMigrateStateResponseData:
    project_root: str
    state_path: str
    backup_path: str | None
    legacy_history_preserved: bool
    legacy_history_count: int
    added_keys: list[str] = field(default_factory=list)
    state_regime: str = ''
    trust_level: str = ''
    blockers: list[str] = field(default_factory=list)
    last_artifacts: list[str] = field(default_factory=list)
    recommended_next_workflow: str | None = None
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class BmadMigrateStateResponse:
    success: bool
    data: BmadMigrateStateResponseData | None
    warnings: list[Message] = field(default_factory=list)
    errors: list[Message] = field(default_factory=list)