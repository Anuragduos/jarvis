from __future__ import annotations

from jarvis_assistant.ai.nlp_engine import NLPEngine
from jarvis_assistant.ai.reasoning import ReasoningEngine
from jarvis_assistant.automation.executor import AutomationExecutor
from jarvis_assistant.memory.context_manager import ContextManager
from jarvis_assistant.security.permissions import PermissionManager

from .config import AppConfig
from .decision_engine import ModeDecisionEngine
from .models import AssistantResponse


class JarvisAssistant:
    def __init__(
        self,
        config: AppConfig,
        nlp: NLPEngine,
        reasoning: ReasoningEngine,
        executor: AutomationExecutor,
        context: ContextManager,
        permissions: PermissionManager,
        decision_engine: ModeDecisionEngine,
    ) -> None:
        self.config = config
        self.nlp = nlp
        self.reasoning = reasoning
        self.executor = executor
        self.context = context
        self.permissions = permissions
        self.decision_engine = decision_engine

    def handle_text(self, text: str) -> AssistantResponse:
        intent = self.nlp.parse(text)
        complexity = self.reasoning.estimate_complexity(text, intent)
        decision = self.decision_engine.decide(
            mode=self.config.mode,
            intent=intent,
            is_sensitive=self.permissions.is_sensitive_intent(intent.intent),
            complexity_score=complexity,
        )
        plan = self.reasoning.create_plan(text=text, intent=intent, route=decision.route)
        if plan.requires_confirmation and not self.permissions.confirm(plan.name):
            return AssistantResponse(text="Cancelled by safety policy.", executed=False)

        result = self.executor.execute_plan(plan)
        self.context.record_interaction(text=text, intent=intent, result=result)
        return AssistantResponse(
            text=result.get("message", "Done."),
            executed=result.get("success", False),
            metadata={"route": decision.route, "reason": decision.reason},
        )
