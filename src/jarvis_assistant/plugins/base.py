from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PluginMetadata:
    """Plugin descriptor metadata."""

    name: str
    version: str
    description: str


class PluginBase(ABC):
    """Plugin interface contract."""

    metadata: PluginMetadata

    @abstractmethod
    def initialize(self) -> None:
        """Performs plugin startup initialization."""

    @abstractmethod
    def can_handle(self, command: str) -> bool:
        """Returns whether plugin can handle command."""

    @abstractmethod
    def handle(self, command: str, context: dict[str, Any]) -> dict[str, Any]:
        """Executes plugin command."""
