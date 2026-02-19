from __future__ import annotations

from typing import Iterable


class VectorMemory:
    """FAISS wrapper placeholder for semantic recall."""

    def __init__(self) -> None:
        self._items: list[tuple[list[float], str]] = []

    def add(self, embedding: list[float], text: str) -> None:
        self._items.append((embedding, text))

    def search(self, embedding: list[float], limit: int = 5) -> Iterable[str]:
        # Placeholder distance scoring.
        del embedding
        return [text for _, text in self._items[:limit]]
