from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class StoryDocument:
    path: str
    story_key: str
    title: str
    status: str
    sections: dict[str, str] = field(default_factory=dict)
    raw_text: str = ''


@dataclass(slots=True)
class SprintStatusEntry:
    key: str
    entry_type: str
    status: str


@dataclass(slots=True)
class SprintStatusDocument:
    path: str
    metadata: dict[str, Any] = field(default_factory=dict)
    development_status: list[SprintStatusEntry] = field(default_factory=list)
    raw_text: str = ''


@dataclass(slots=True)
class NormalizedState:
    project_root: str
    state_regime: str
    trust_level: str
    normalized_state: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ArtifactContractSummary:
    artifact_type: str
    contract_version: str
    display_name: str
    phase: str
    format: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ReviewRecordDocument:
    path: str
    story_key: str
    review_type: str
    status: str
    sections: dict[str, str] = field(default_factory=dict)
    raw_text: str = ''


@dataclass(slots=True)
class QARecordDocument:
    path: str
    story_key: str
    qa_type: str
    status: str
    sections: dict[str, str] = field(default_factory=dict)
    raw_text: str = ''


# ---------------------------------------------------------------------------
# Phase 1 — Analysis artifacts
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class BrainstormingSessionDocument:
    path: str
    session_name: str
    status: str
    sections: dict[str, str] = field(default_factory=dict)
    raw_text: str = ''


@dataclass(slots=True)
class ProductBriefDocument:
    path: str
    project_name: str
    status: str
    sections: dict[str, str] = field(default_factory=dict)
    raw_text: str = ''


@dataclass(slots=True)
class PRFAQDocument:
    path: str
    project_name: str
    status: str
    sections: dict[str, str] = field(default_factory=dict)
    raw_text: str = ''


# ---------------------------------------------------------------------------
# Phase 2 — Planning artifacts
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class PRDDocument:
    path: str
    project_name: str
    status: str
    sections: dict[str, str] = field(default_factory=dict)
    raw_text: str = ''


@dataclass(slots=True)
class PRDValidationReportDocument:
    path: str
    project_name: str
    status: str
    validation_type: str
    sections: dict[str, str] = field(default_factory=dict)
    raw_text: str = ''


@dataclass(slots=True)
class UXDesignDocument:
    path: str
    project_name: str
    status: str
    sections: dict[str, str] = field(default_factory=dict)
    raw_text: str = ''


# ---------------------------------------------------------------------------
# Phase 3 — Solutioning artifacts
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class ArchitectureDocument:
    path: str
    project_name: str
    status: str
    sections: dict[str, str] = field(default_factory=dict)
    raw_text: str = ''


@dataclass(slots=True)
class EpicsAndStoriesDocument:
    path: str
    project_name: str
    status: str
    sections: dict[str, str] = field(default_factory=dict)
    raw_text: str = ''


@dataclass(slots=True)
class ProjectContextDocument:
    path: str
    project_name: str
    sections: dict[str, str] = field(default_factory=dict)
    raw_text: str = ''
