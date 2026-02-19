from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from jarvis_assistant.core.config import MemoryConfig


class MemoryStore:
    def __init__(self, config: MemoryConfig) -> None:
        self.config = config
        self.config.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.config.sqlite_path)
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                intent TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        self.conn.commit()

    def add_interaction(self, text: str, intent: str, result: dict[str, Any]) -> None:
        self.conn.execute(
            "INSERT INTO interactions(text, intent, result) VALUES (?, ?, ?)",
            (text, intent, json.dumps(result)),
        )
        self.conn.commit()

    def set_preference(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO preferences(key, value) VALUES (?, ?)",
            (key, value),
        )
        self.conn.commit()
