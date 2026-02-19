from __future__ import annotations


class EmotionalToneDetector:
    """Detects tone and urgency/stress hints from text."""

    POSITIVE = {"great", "awesome", "thanks", "love"}
    NEGATIVE = {"bad", "hate", "frustrated", "angry"}
    URGENT = {"urgent", "immediately", "asap", "now"}
    STRESS = {"stressed", "overwhelmed", "panic", "anxious"}

    def detect(self, text: str) -> str:
        """Returns tone classification."""

        words = set(text.lower().split())
        if words & self.NEGATIVE:
            return "negative"
        if words & self.POSITIVE:
            return "positive"
        return "neutral"

    def detect_urgency_and_stress(self, text: str) -> dict[str, bool]:
        """Returns urgency and stress boolean markers."""

        words = set(text.lower().split())
        return {"urgent": bool(words & self.URGENT), "stressed": bool(words & self.STRESS)}


class AdaptivePersonality:
    """Applies response style transformations based on tone and user mode."""

    def __init__(self, level: float = 0.5, formal_mode: bool = True) -> None:
        self.level = max(0.0, min(1.0, level))
        self.formal_mode = formal_mode

    def apply_style(self, text: str, tone: str) -> str:
        """Returns styled response text."""

        if self.level < 0.3:
            return text
        prefix = ""
        if tone == "negative":
            prefix = "I understand. "
        elif tone == "positive":
            prefix = "Excellent. "
        if not self.formal_mode:
            return (prefix + text).replace("I understand.", "Got it,").replace("Excellent.", "Nice,")
        return prefix + text
