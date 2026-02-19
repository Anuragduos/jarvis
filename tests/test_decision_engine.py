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
