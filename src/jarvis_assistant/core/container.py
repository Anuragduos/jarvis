from __future__ import annotations

from jarvis_assistant.ai.nlp_engine import NLPEngine
from jarvis_assistant.ai.reasoning import ReasoningEngine
from jarvis_assistant.automation.executor import AutomationExecutor
from jarvis_assistant.memory.context_manager import ContextManager
from jarvis_assistant.memory.store import MemoryStore
from jarvis_assistant.security.permissions import PermissionManager

from .assistant import JarvisAssistant
from .config import AppConfig
from .decision_engine import ModeDecisionEngine


class ServiceContainer:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.memory_store = MemoryStore(config.memory)
        self.context_manager = ContextManager(self.memory_store)
        self.permissions = PermissionManager(config.security)
        self.nlp = NLPEngine()
        self.reasoning = ReasoningEngine(config=config)
        self.executor = AutomationExecutor(permission_manager=self.permissions)
        self.decision = ModeDecisionEngine()

    def build_assistant(self) -> JarvisAssistant:
        return JarvisAssistant(
            config=self.config,
            nlp=self.nlp,
            reasoning=self.reasoning,
            executor=self.executor,
            context=self.context_manager,
            permissions=self.permissions,
            decision_engine=self.decision,
        )
