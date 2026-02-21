from __future__ import annotations

import logging

from jarvis_assistant.core.config import AppConfig, ExecutionMode


class PermissionManager:
    """Permission and policy checks for sensitive automation and plugins."""

    def __init__(self, config: AppConfig, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger
        self.sensitive_intents = {"email_send", "delete_file", "system_shutdown"}
        self.command_blacklist = {"rm", "mkfs", "shutdown"}
        self.plugin_denylist = {"developer_tools"} if config.execution_mode == ExecutionMode.SAFE_MODE else set()

    def is_sensitive_intent(self, intent: str) -> bool:
        """Returns whether intent is sensitive."""

        return intent in self.sensitive_intents

    def confirm(self, action_name: str) -> bool:
        """Confirmation hook for dangerous actions."""

        self.logger.info("confirmation_requested action=%s", action_name)
        return True

    def is_command_allowed(self, command: str) -> bool:
        """Checks command policy with SAFE_MODE enforcement."""

        if self.config.execution_mode == ExecutionMode.SAFE_MODE:
            return False
        blocked = any(command.startswith(prefix) for prefix in self.command_blacklist)
        return not blocked

    def is_plugin_allowed(self, plugin_name: str) -> bool:
        """Checks if plugin is allowed by policy."""

        if self.config.execution_mode == ExecutionMode.SAFE_MODE:
            return False
        return plugin_name not in self.plugin_denylist
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
