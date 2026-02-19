from __future__ import annotations

import importlib.util
import logging
import shutil
import sqlite3
import socket
from pathlib import Path
from typing import Any

from jarvis_assistant.contracts.results import DiagnosticReport, ResultStatus
from jarvis_assistant.core.config import AppConfig
from jarvis_assistant.infrastructure.hardware_profiler import HardwareProfile


class SelfDiagnostics:
    """Startup self-diagnostics service."""

    def __init__(
        self,
        config: AppConfig,
        plugin_registry: dict[str, Any],
        hardware_profile: HardwareProfile,
        logger: logging.Logger,
    ) -> None:
        self.config = config
        self.plugin_registry = plugin_registry
        self.hardware_profile = hardware_profile
        self.logger = logger

    def run(self) -> DiagnosticReport:
        """Runs diagnostics and returns structured report."""

        checks = {
            "python_available": True,
            "whisper_importable": importlib.util.find_spec("whisper") is not None,
            "ollama_installed": shutil.which("ollama") is not None,
            "cloud_connectivity": self._check_cloud_connectivity(),
            "plugins_loaded": len(self.plugin_registry) > 0,
            "db_integrity": self._check_db_integrity(),
            "hardware_sufficient": self.hardware_profile.ram_gb >= 4,
            "config_consistency": self.config.request_timeout_seconds > 0,
        }
        passed = sum(1 for value in checks.values() if value)
        confidence = passed / len(checks)
        status = ResultStatus.SUCCESS if confidence >= 0.8 else ResultStatus.PARTIAL
        self.logger.info("diagnostics checks=%s", checks)
        return DiagnosticReport(status=status, confidence=confidence, checks=checks)

    def _check_cloud_connectivity(self) -> bool:
        try:
            with socket.create_connection(("api.openai.com", 443), timeout=1.5):
                return True
        except OSError:
            return False

    def _check_db_integrity(self) -> bool:
        try:
            self.config.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.config.sqlite_path)
            row = conn.execute("PRAGMA integrity_check;").fetchone()
            conn.close()
            return bool(row and row[0] == "ok")
        except sqlite3.Error:
            return False
