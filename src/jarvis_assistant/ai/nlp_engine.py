from __future__ import annotations

import re
from dataclasses import dataclass

from jarvis_assistant.core.models import IntentResult


@dataclass
class Rule:
    pattern: str
    intent: str


class NLPEngine:
    """Hybrid NLP pipeline: simple preprocessing + rule fallback + classifier stub."""

    def __init__(self) -> None:
        self.rules = [
            Rule(pattern=r"\b(open|launch)\b", intent="open_app"),
            Rule(pattern=r"\b(close|quit)\b", intent="close_app"),
            Rule(pattern=r"\b(weather)\b", intent="weather_query"),
            Rule(pattern=r"\b(schedule|remind)\b", intent="create_reminder"),
        ]

    def parse(self, text: str) -> IntentResult:
        normalized = text.lower().strip()
        for rule in self.rules:
            if re.search(rule.pattern, normalized):
                return IntentResult(intent=rule.intent, confidence=0.82, raw_text=text)

        return IntentResult(intent="general_reasoning", confidence=0.48, raw_text=text)
