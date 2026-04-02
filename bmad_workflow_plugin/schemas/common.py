from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ArtifactType(str, Enum):
    # Phase 1 — Analysis
    BRAINSTORMING_SESSION = 'brainstorming_session'
    PRODUCT_BRIEF = 'product_brief'
    PRFAQ = 'prfaq'
    # Phase 2 — Planning
    PRD = 'prd'
    PRD_VALIDATION_REPORT = 'prd_validation_report'
    UX_DESIGN = 'ux_design'
    # Phase 3 — Solutioning
    ARCHITECTURE = 'architecture'
    EPICS_AND_STORIES = 'epics_and_stories'
    PROJECT_CONTEXT = 'project_context'
    # Phase 4 — Implementation
    STORY = 'story'
    SPRINT_STATUS = 'sprint_status'
    REVIEW_RECORD = 'review_record'
    QA_RECORD = 'qa_record'


class WorkflowId(str, Enum):
    CREATE_STORY = 'create-story'
    DEV_STORY = 'dev-story'
    CODE_REVIEW = 'code-review'
    QA_GATE = 'qa-gate'
    CORRECT_COURSE = 'correct-course'
    SPRINT_PLANNING = 'sprint-planning'
    PROJECT_INIT = 'project-init'
    STATE_MIGRATION = 'state-migration'
    STATE_CHECK = 'state-check'
    RETROSPECTIVE = 'retrospective'


class StateRegime(str, Enum):
    MISSING = 'missing'
    LEGACY_ONLY = 'legacy_only'
    PARTIALLY_NORMALIZED = 'partially_normalized'
    NORMALIZED_STALE = 'normalized_stale'
    NORMALIZED_READY = 'normalized_ready'


class TrustLevel(str, Enum):
    HIGH = 'high'
    PARTIAL = 'partial'
    LOW = 'low'


class StoryStatus(str, Enum):
    BACKLOG = 'backlog'
    READY_FOR_DEV = 'ready-for-dev'
    IN_PROGRESS = 'in-progress'
    REVIEW = 'review'
    DONE = 'done'
    BLOCKED = 'blocked'


class SprintEntryType(str, Enum):
    EPIC = 'epic'
    STORY = 'story'
    RETROSPECTIVE = 'retrospective'


@dataclass(slots=True)
class Message:
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ValidationResult:
    valid: bool
    errors: list[Message] = field(default_factory=list)
    warnings: list[Message] = field(default_factory=list)
    parsed_summary: dict[str, Any] | None = None


@dataclass(slots=True)
class UpdateResult:
    updated: bool
    path: str | None
    notes: list[str] = field(default_factory=list)
