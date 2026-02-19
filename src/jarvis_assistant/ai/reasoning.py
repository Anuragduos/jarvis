from __future__ import annotations

from jarvis_assistant.cloud.model_router import ModelRouter
from jarvis_assistant.core.config import AppConfig
from jarvis_assistant.core.models import ActionPlan, IntentResult


class ReasoningEngine:
    def __init__(self, config: AppConfig) -> None:
        self.router = ModelRouter(config.model)

    def estimate_complexity(self, text: str, intent: IntentResult) -> float:
        tokens = len(text.split())
        heuristic = min(1.0, tokens / 24)
        if intent.intent == "general_reasoning":
            heuristic = max(heuristic, 0.7)
        return heuristic

    def create_plan(self, text: str, intent: IntentResult, route: str) -> ActionPlan:
        if intent.intent in {"open_app", "close_app"}:
            return ActionPlan(
                name=intent.intent,
                steps=[{"type": "system", "intent": intent.intent, "text": text}],
                requires_confirmation=False,
            )

        if intent.intent == "create_reminder":
            return ActionPlan(
                name="create_reminder",
                steps=[{"type": "plugin", "name": "smart_reminders", "payload": text}],
            )

        answer = self.router.generate(text=text, route=route)
        return ActionPlan(
            name="respond_only",
            steps=[{"type": "response", "message": answer}],
            sensitive=False,
        )
