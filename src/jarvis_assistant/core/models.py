from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AssistantMode(str, Enum):
    """Execution modes supported by routing."""

    OFFLINE = "offline"
    ONLINE = "online"
    HYBRID = "hybrid"
    SAFE_MODE = "safe_mode"


@dataclass(slots=True)
class IntentResult:
    """Intent extraction output."""

    OFFLINE = "offline"
    ONLINE = "online"
    HYBRID = "hybrid"


@dataclass
class IntentResult:
    intent: str
    confidence: float
    entities: dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""


@dataclass(slots=True)
class ActionPlan:
    """Executable action plan."""

@dataclass
class ActionPlan:
    name: str
    steps: list[dict[str, Any]]
    requires_confirmation: bool = False
    sensitive: bool = False


@dataclass(slots=True)
class AssistantResponse:
    """Assistant response payload for UI/CLI."""

@dataclass
class AssistantResponse:
    text: str
    executed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
