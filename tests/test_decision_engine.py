import logging

from jarvis_assistant.core.config import ExecutionMode
from jarvis_assistant.core.decision_engine import ModeDecisionEngine
from jarvis_assistant.core.models import IntentResult
from jarvis_assistant.infrastructure.circuit_breaker import CircuitState


def test_sensitive_routes_local() -> None:
    engine = ModeDecisionEngine(logging.getLogger("test"))
    intent = IntentResult(intent="delete_file", confidence=0.9)
    decision = engine.decide(
        ExecutionMode.HYBRID,
        intent,
        is_sensitive=True,
        complexity_score=0.8,
        circuit_state=CircuitState(is_open=False, failure_count=0, opened_until=None),
    )
    assert decision.route == "local"


def test_circuit_open_routes_local() -> None:
    engine = ModeDecisionEngine(logging.getLogger("test"))
    intent = IntentResult(intent="general_reasoning", confidence=0.4)
    decision = engine.decide(
        ExecutionMode.HYBRID,
        intent,
        is_sensitive=False,
        complexity_score=0.9,
        circuit_state=CircuitState(is_open=True, failure_count=3, opened_until=9999999999.0),
    )
    assert decision.route == "local"
from jarvis_assistant.core.decision_engine import ModeDecisionEngine
from jarvis_assistant.core.models import AssistantMode, IntentResult


def test_sensitive_routes_local() -> None:
    engine = ModeDecisionEngine()
    intent = IntentResult(intent="delete_file", confidence=0.9)
    decision = engine.decide(AssistantMode.HYBRID, intent, is_sensitive=True, complexity_score=0.8)
    assert decision.route == "local"


def test_complex_routes_cloud() -> None:
    engine = ModeDecisionEngine()
    intent = IntentResult(intent="general_reasoning", confidence=0.4)
    decision = engine.decide(AssistantMode.HYBRID, intent, is_sensitive=False, complexity_score=0.9)
    assert decision.route == "cloud"
