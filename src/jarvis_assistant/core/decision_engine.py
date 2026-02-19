from __future__ import annotations

from dataclasses import dataclass

from .models import AssistantMode, IntentResult


@dataclass
class Decision:
    route: str
    reason: str


class ModeDecisionEngine:
    """Routes tasks between local and cloud providers."""

    def decide(
        self,
        mode: AssistantMode,
        intent: IntentResult,
        is_sensitive: bool,
        complexity_score: float,
    ) -> Decision:
        if mode == AssistantMode.OFFLINE:
            return Decision(route="local", reason="manual_offline_mode")

        if mode == AssistantMode.ONLINE and not is_sensitive:
            return Decision(route="cloud", reason="manual_online_mode")

        if is_sensitive:
            return Decision(route="local", reason="sensitive_task")

        if complexity_score < 0.45 and intent.confidence >= 0.7:
            return Decision(route="local", reason="simple_task")

        return Decision(route="cloud", reason="complex_or_low_confidence")
