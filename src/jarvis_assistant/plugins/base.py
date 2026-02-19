from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class PluginMetadata:
    name: str
    version: str
    description: str


class PluginBase(ABC):
    metadata: PluginMetadata

    @abstractmethod
    def initialize(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def can_handle(self, command: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def handle(self, command: str, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
