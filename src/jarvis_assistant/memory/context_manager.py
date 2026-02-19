from __future__ import annotations

from jarvis_assistant.core.models import IntentResult

from .store import MemoryStore


class ContextManager:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def record_interaction(self, text: str, intent: IntentResult, result: dict) -> None:
        self.store.add_interaction(text=text, intent=intent.intent, result=result)
