from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from jarvis_assistant.core.models import IntentResult


@dataclass(slots=True)
class Rule:
    """Fallback rule parser entry."""

@dataclass
class Rule:
    pattern: str
    intent: str


class NLPEngine:
    """Hybrid NLP pipeline: lightweight preprocessing + rule fallback."""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
    """Hybrid NLP pipeline: simple preprocessing + rule fallback + classifier stub."""

    def __init__(self) -> None:
        self.rules = [
            Rule(pattern=r"\b(open|launch)\b", intent="open_app"),
            Rule(pattern=r"\b(close|quit)\b", intent="close_app"),
            Rule(pattern=r"\b(weather)\b", intent="weather_query"),
            Rule(pattern=r"\b(schedule|remind)\b", intent="create_reminder"),
        ]

    def parse(self, text: str) -> IntentResult:
        """Parses input text into an intent object."""

        normalized = text.lower().strip()
        for rule in self.rules:
            if re.search(rule.pattern, normalized):
                self.logger.debug("rule_match intent=%s", rule.intent)
                return IntentResult(intent=rule.intent, confidence=0.82, raw_text=text)

        self.logger.debug("rule_match intent=general_reasoning")
        normalized = text.lower().strip()
        for rule in self.rules:
            if re.search(rule.pattern, normalized):
                return IntentResult(intent=rule.intent, confidence=0.82, raw_text=text)

        return IntentResult(intent="general_reasoning", confidence=0.48, raw_text=text)
