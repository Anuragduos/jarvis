from __future__ import annotations

import logging
from dataclasses import dataclass

from jarvis_assistant.core.config import ExecutionMode
from jarvis_assistant.infrastructure.circuit_breaker import CircuitState

from .models import IntentResult


@dataclass(slots=True)
class Decision:
    """Routing decision result."""

from dataclasses import dataclass

from .models import AssistantMode, IntentResult


@dataclass
class Decision:
    route: str
    reason: str


class ModeDecisionEngine:
    """Routes tasks between local and cloud providers."""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def decide(
        self,
        mode: ExecutionMode,
        intent: IntentResult,
        is_sensitive: bool,
        complexity_score: float,
        circuit_state: CircuitState,
    ) -> Decision:
        if mode in {ExecutionMode.OFFLINE, ExecutionMode.SAFE_MODE}:
            decision = Decision(route="local", reason="manual_or_safe_mode")
        elif circuit_state.is_open:
            decision = Decision(route="local", reason="cloud_circuit_open")
        elif mode == ExecutionMode.ONLINE and not is_sensitive:
            decision = Decision(route="cloud", reason="manual_online_mode")
        elif is_sensitive:
            decision = Decision(route="local", reason="sensitive_task")
        elif complexity_score < 0.45 and intent.confidence >= 0.7:
            decision = Decision(route="local", reason="simple_task")
        else:
            decision = Decision(route="cloud", reason="complex_or_low_confidence")

        self.logger.info(
            "routing_decision route=%s reason=%s intent=%s complexity=%.2f circuit_open=%s",
            decision.route,
            decision.reason,
            intent.intent,
            complexity_score,
            circuit_state.is_open,
        )
        return decision
    def decide(
        self,
        mode: AssistantMode,
        intent: IntentResult,
        is_sensitive: bool,
        complexity_score: float,
    ) -> Decision:
        if mode == AssistantMode.OFFLINE:
            return Decision(route="local", reason="manual_offline_mode")

        if mode == AssistantMode.ONLINE and not is_sensitive:
            return Decision(route="cloud", reason="manual_online_mode")

        if is_sensitive:
            return Decision(route="local", reason="sensitive_task")

        if complexity_score < 0.45 and intent.confidence >= 0.7:
            return Decision(route="local", reason="simple_task")

        return Decision(route="cloud", reason="complex_or_low_confidence")
