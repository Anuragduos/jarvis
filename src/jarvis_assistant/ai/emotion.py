from __future__ import annotations


class EmotionalToneDetector:
    POSITIVE = {"great", "awesome", "thanks", "love"}
    NEGATIVE = {"bad", "hate", "frustrated", "angry"}

    def detect(self, text: str) -> str:
        words = set(text.lower().split())
        if words & self.NEGATIVE:
            return "negative"
        if words & self.POSITIVE:
            return "positive"
        return "neutral"


class AdaptivePersonality:
    def __init__(self, level: float = 0.5) -> None:
        self.level = max(0.0, min(1.0, level))

    def apply_style(self, text: str, tone: str) -> str:
        if self.level < 0.3:
            return text
        if tone == "negative":
            return f"I understand. {text}"
        if tone == "positive":
            return f"Excellent. {text}"
        return text
