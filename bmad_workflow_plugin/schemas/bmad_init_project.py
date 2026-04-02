from __future__ import annotations

from dataclasses import dataclass, field

from bmad_workflow_plugin.schemas.common import Message


@dataclass(slots=True)
class BmadInitProjectRequest:
    project_root: str
    project_name: str | None = None
    create_core_config: bool = True
    output_folder: str | None = None
    user_name: str | None = None
    communication_language: str | None = None
    document_output_language: str | None = None
    user_skill_level: str | None = None


@dataclass(slots=True)
class BmadInitProjectResponseData:
    project_root: str
    project_name: str
    state_path: str
    notes_path: str
    config_path: str | None
    legacy_output_root: str
    created_paths: list[str] = field(default_factory=list)
    preserved_paths: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class BmadInitProjectResponse:
    success: bool
    data: BmadInitProjectResponseData | None
    warnings: list[Message] = field(default_factory=list)
    errors: list[Message] = field(default_factory=list)
