from __future__ import annotations

from dataclasses import asdict

from jarvis_assistant.contracts.results import ActionResult
from jarvis_assistant.core.models import IntentResult

from .store import MemoryStore


class ContextManager:
    """Writes interaction context into persistent memory."""

    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def record_interaction(self, text: str, intent: IntentResult, result: ActionResult) -> None:
        """Records interaction and structured result."""

        self.store.add_interaction(text=text, intent=intent.intent, result=asdict(result))
        tone = result.metadata.get("tone")
        if isinstance(tone, str):
            self.store.set_preference("last_tone", tone)
