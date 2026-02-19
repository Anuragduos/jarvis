from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AssistantMode(str, Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    HYBRID = "hybrid"


@dataclass
class IntentResult:
    intent: str
    confidence: float
    entities: dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""


@dataclass
class ActionPlan:
    name: str
    steps: list[dict[str, Any]]
    requires_confirmation: bool = False
    sensitive: bool = False


@dataclass
class AssistantResponse:
    text: str
    executed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
