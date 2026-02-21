from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol


class Rollbackable(Protocol):
    """Protocol for rollback-capable actions."""

    def rollback(self) -> bool:
        """Rolls back the action."""


@dataclass(slots=True)
class JournalEntry:
    """Execution journal entry."""

    action: str
    payload: dict[str, Any]
    reversible: bool
    deleted: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))


class CommandHistoryRegistry:
    """Tracks command execution and supports soft delete + rollback dispatch."""

    def __init__(self) -> None:
        self.entries: list[JournalEntry] = []
        self._rollback_stack: list[Rollbackable] = []

    def record(self, action: str, payload: dict[str, Any], reversible: bool = False) -> None:
        self.entries.append(JournalEntry(action=action, payload=payload, reversible=reversible))

    def register_rollback(self, rollbackable: Rollbackable) -> None:
        self._rollback_stack.append(rollbackable)

    def soft_delete_last(self) -> bool:
        if not self.entries:
            return False
        self.entries[-1].deleted = True
        return True

    def rollback_last(self) -> bool:
        if not self._rollback_stack:
            return False
        op = self._rollback_stack.pop()
        return op.rollback()
