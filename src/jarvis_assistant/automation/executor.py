from __future__ import annotations

import concurrent.futures
import logging
import subprocess
from dataclasses import dataclass, field
from typing import Any

from jarvis_assistant.contracts.results import ActionResult, ErrorInfo, ReasoningResult, ResultStatus
from jarvis_assistant.infrastructure.errors import ErrorBoundary
from jarvis_assistant.infrastructure.rate_limiter import SlidingWindowLimiter
from jarvis_assistant.plugins.base import PluginBase
from jarvis_assistant.security.permissions import PermissionManager
from jarvis_assistant.transactions.undo import CommandHistoryRegistry


@dataclass(slots=True)
class ExecutionLog:
    """In-memory execution audit log."""

    entries: list[dict[str, Any]] = field(default_factory=list)


class AutomationExecutor:
    """Executes action plans with safety, plugin isolation, and journaling."""

    def __init__(
        self,
        permission_manager: PermissionManager,
        history: CommandHistoryRegistry,
        error_boundary: ErrorBoundary,
        logger: logging.Logger,
        plugin_registry: dict[str, PluginBase],
        plugin_timeout_seconds: float,
        automation_limiter: SlidingWindowLimiter,
        plugin_limiter: SlidingWindowLimiter,
    ) -> None:
        self.permissions = permission_manager
        self.log = ExecutionLog()
        self.history = history
        self.error_boundary = error_boundary
        self.logger = logger
        self.plugin_registry = plugin_registry
        self.plugin_timeout_seconds = plugin_timeout_seconds
        self.automation_limiter = automation_limiter
        self.plugin_limiter = plugin_limiter

    def execute_plan(self, plan: ReasoningResult) -> ActionResult:
        """Executes a structured reasoning plan."""

        if not self.automation_limiter.allow():
            return ActionResult(
                status=ResultStatus.FAILED,
                confidence=0.0,
                message="Automation rate limit exceeded.",
                error=ErrorInfo(code="AUTOMATION_RATE_LIMIT", message="Automation rate limit exceeded."),
            )

        for step in plan.steps:
            stype = step.get("type")
            if stype == "response":
                return ActionResult(
                    status=ResultStatus.SUCCESS,
                    confidence=plan.confidence,
                    message=step.get("message", "Done"),
                    metadata={"kind": "response"},
                )
            if stype == "system":
                return self._execute_system(step)
            if stype == "plugin":
                return self._execute_plugin(step)

        return ActionResult(
            status=ResultStatus.FAILED,
            confidence=0.0,
            message="No executable steps.",
            error=ErrorInfo(code="NO_STEPS", message="Plan contained no executable steps."),
        )

    def _execute_plugin(self, step: dict[str, Any]) -> ActionResult:
        plugin_name = str(step.get("name", ""))
        payload = str(step.get("payload", ""))
        self.logger.info("plugin_execute_start plugin=%s", plugin_name)

        if not self.plugin_limiter.allow():
            return ActionResult(
                status=ResultStatus.FAILED,
                confidence=0.0,
                message="Plugin rate limit exceeded.",
                error=ErrorInfo(code="PLUGIN_RATE_LIMIT", message="Plugin rate limit exceeded."),
            )

        plugin = self.plugin_registry.get(plugin_name)
        if plugin is None:
            return ActionResult(
                status=ResultStatus.FAILED,
                confidence=0.0,
                message=f"Plugin '{plugin_name}' not found.",
                error=ErrorInfo(code="PLUGIN_NOT_FOUND", message=f"Plugin '{plugin_name}' not found."),
            )

        if not self.permissions.is_plugin_allowed(plugin_name):
            return ActionResult(
                status=ResultStatus.FAILED,
                confidence=0.0,
                message=f"Plugin '{plugin_name}' blocked by policy.",
                error=ErrorInfo(code="PLUGIN_BLOCKED", message="Plugin blocked by permission policy."),
            )

        def run_plugin() -> dict[str, Any]:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(plugin.handle, payload, {"step": step})
                return future.result(timeout=self.plugin_timeout_seconds)

        result = self.error_boundary.safe_call(
            run_plugin,
            fallback=lambda err: {"success": False, "message": err.message, "error": err.code},
        )
        success = bool(result.get("success", False))
        self.logger.info("plugin_execute_finish plugin=%s success=%s", plugin_name, success)
        return ActionResult(
            status=ResultStatus.SUCCESS if success else ResultStatus.FAILED,
            confidence=0.7 if success else 0.0,
            message=str(result.get("message", "Plugin execution completed.")),
            metadata={"plugin": plugin_name, "plugin_result": result},
            error=None if success else ErrorInfo(code="PLUGIN_EXECUTION", message=str(result.get("message", ""))),
        )

    def _execute_system(self, step: dict[str, Any]) -> ActionResult:
        intent = step.get("intent")
        text = step.get("text", "")
        self.log.entries.append({"intent": intent, "text": text})

        if intent == "open_app":
            app = text.split()[-1]
            if not self.permissions.is_command_allowed(app):
                return ActionResult(
                    status=ResultStatus.FAILED,
                    confidence=0.0,
                    message="Blocked by command policy.",
                    error=ErrorInfo(code="POLICY_BLOCK", message="Command not allowed."),
                )
            subprocess.Popen([app])
            self.history.record(action="open_app", payload={"app": app}, reversible=True)
            self.logger.info("opened_app app=%s", app)
            return ActionResult(status=ResultStatus.SUCCESS, confidence=0.8, message=f"Opened {app}.")

        if intent == "close_app":
            self.history.record(action="close_app", payload={"text": text}, reversible=False)
            return ActionResult(status=ResultStatus.SUCCESS, confidence=0.75, message="Close app action acknowledged.")

        return ActionResult(
            status=ResultStatus.FAILED,
            confidence=0.0,
            message=f"Unsupported system intent: {intent}",
            error=ErrorInfo(code="UNSUPPORTED_INTENT", message=f"Unsupported system intent: {intent}"),
        )
