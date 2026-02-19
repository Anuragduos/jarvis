from __future__ import annotations

from jarvis_assistant.core.config import SecurityConfig


class PermissionManager:
    def __init__(self, config: SecurityConfig) -> None:
        self.config = config
        self.sensitive_intents = {"email_send", "delete_file", "system_shutdown"}

    def is_sensitive_intent(self, intent: str) -> bool:
        return intent in self.sensitive_intents

    def confirm(self, action_name: str) -> bool:
        # Hook this into UI dialog in production.
        del action_name
        return True
