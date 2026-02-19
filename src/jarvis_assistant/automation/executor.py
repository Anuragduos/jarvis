from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import Any

from jarvis_assistant.core.models import ActionPlan
from jarvis_assistant.security.permissions import PermissionManager


@dataclass
class ExecutionLog:
    entries: list[dict[str, Any]] = field(default_factory=list)


class AutomationExecutor:
    def __init__(self, permission_manager: PermissionManager) -> None:
        self.permissions = permission_manager
        self.log = ExecutionLog()
        self.undo_stack: list[dict[str, Any]] = []

    def execute_plan(self, plan: ActionPlan) -> dict[str, Any]:
        for step in plan.steps:
            stype = step.get("type")
            if stype == "response":
                return {"success": True, "message": step.get("message", "Done")}
            if stype == "system":
                return self._execute_system(step)
            if stype == "plugin":
                return {"success": True, "message": f"Plugin call queued: {step.get('name')}"}

        return {"success": False, "message": "No executable steps."}

    def _execute_system(self, step: dict[str, Any]) -> dict[str, Any]:
        intent = step.get("intent")
        text = step.get("text", "")
        self.log.entries.append({"intent": intent, "text": text})

        if intent == "open_app":
            app = text.split()[-1]
            subprocess.Popen([app])
            self.undo_stack.append({"type": "close_app", "app": app})
            return {"success": True, "message": f"Opened {app}."}

        if intent == "close_app":
            return {"success": True, "message": "Close app action acknowledged."}

        return {"success": False, "message": f"Unsupported system intent: {intent}"}

    def undo_last(self) -> dict[str, Any]:
        if not self.undo_stack:
            return {"success": False, "message": "Nothing to undo."}
        action = self.undo_stack.pop()
        return {"success": True, "message": f"Undo placeholder: {action}"}
