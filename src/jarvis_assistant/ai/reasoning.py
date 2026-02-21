from __future__ import annotations

import logging

from jarvis_assistant.cloud.model_router import ModelRouter
from jarvis_assistant.contracts.results import ErrorInfo, ReasoningResult, ResultStatus
from jarvis_assistant.core.models import IntentResult


class ReasoningEngine:
    """Reasoning and task planning service."""

    def __init__(self, router: ModelRouter, logger: logging.Logger) -> None:
        self.router = router
        self.logger = logger

    def estimate_complexity(self, text: str, intent: IntentResult) -> float:
        """Estimates prompt complexity for routing."""

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

    async def create_plan(self, text: str, intent: IntentResult, route: str) -> ReasoningResult:
        """Creates a structured reasoning result containing plan steps."""

        if intent.intent in {"open_app", "close_app"}:
            return ReasoningResult(
                status=ResultStatus.SUCCESS,
                confidence=0.8,
                plan_name=intent.intent,
                steps=[{"type": "system", "intent": intent.intent, "text": text}],
                metadata={"requires_confirmation": False},
            )

        if intent.intent == "create_reminder":
            return ReasoningResult(
                status=ResultStatus.SUCCESS,
                confidence=0.75,
                plan_name="create_reminder",
                steps=[{"type": "plugin", "name": "smart_reminders", "payload": text}],
                metadata={"requires_confirmation": False},
            )

        answer = await self.router.generate(text=text, route=route)
        if not answer:
            return ReasoningResult(
                status=ResultStatus.FAILED,
                confidence=0.0,
                plan_name="respond_only",
                error=ErrorInfo(code="NO_RESPONSE", message="Reasoning provider returned empty response."),
            )

        return ReasoningResult(
            status=ResultStatus.SUCCESS,
            confidence=0.6,
            plan_name="respond_only",
            steps=[{"type": "response", "message": answer}],
            metadata={"requires_confirmation": False},
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
