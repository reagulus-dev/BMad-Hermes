from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ArtifactContract:
    artifact_type: str
    contract_version: str
    display_name: str
    phase: str
    format: str
    raw: dict[str, Any] = field(default_factory=dict)
