from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ExecutionMode(str, Enum):
    """Allowed execution modes."""

    OFFLINE = "offline"
    ONLINE = "online"
    HYBRID = "hybrid"
    SAFE_MODE = "safe_mode"


@dataclass(slots=True)
class AppConfig:
    """Validated application configuration loaded from environment."""

    execution_mode: ExecutionMode = ExecutionMode.HYBRID
    log_level: str = "INFO"
    log_file: Path = Path("logs/jarvis.log")
    sqlite_path: Path = Path("data/memory.db")
    encrypted_key_file: Path = Path(".secrets/master.key")
    encrypted_data_file: Path = Path(".secrets/api_keys.enc")

    max_workers: int = 4
    request_timeout_seconds: float = 20.0
    plugin_timeout_seconds: float = 5.0

    request_rate_limit_per_minute: int = 120
    cloud_rate_limit_per_minute: int = 30
    automation_rate_limit_per_minute: int = 60
    plugin_rate_limit_per_minute: int = 60

    cloud_failure_threshold: int = 3
    cloud_cooldown_seconds: float = 30.0
    cloud_provider: str = "openai"

    def validate(self) -> None:
        """Validates config values with explicit error messages."""

        if not (1 <= self.max_workers <= 64):
            raise RuntimeError("Invalid configuration: max_workers must be between 1 and 64.")
        if self.request_timeout_seconds <= 0:
            raise RuntimeError("Invalid configuration: request_timeout_seconds must be > 0.")
        if self.plugin_timeout_seconds <= 0:
            raise RuntimeError("Invalid configuration: plugin_timeout_seconds must be > 0.")


def load_config() -> AppConfig:
    """Loads and validates config from environment variables."""

    raw_mode = os.getenv("JARVIS_EXECUTION_MODE", ExecutionMode.HYBRID.value)
    try:
        mode = ExecutionMode(raw_mode)
    except ValueError as exc:
        raise RuntimeError(f"Invalid configuration: unsupported execution mode '{raw_mode}'.") from exc

    cfg = AppConfig(
        execution_mode=mode,
        log_level=os.getenv("JARVIS_LOG_LEVEL", "INFO"),
        log_file=Path(os.getenv("JARVIS_LOG_FILE", "logs/jarvis.log")),
        sqlite_path=Path(os.getenv("JARVIS_SQLITE_PATH", "data/memory.db")),
        encrypted_key_file=Path(os.getenv("JARVIS_ENCRYPTED_KEY_FILE", ".secrets/master.key")),
        encrypted_data_file=Path(os.getenv("JARVIS_ENCRYPTED_DATA_FILE", ".secrets/api_keys.enc")),
        max_workers=int(os.getenv("JARVIS_MAX_WORKERS", "4")),
        request_timeout_seconds=float(os.getenv("JARVIS_REQUEST_TIMEOUT_SECONDS", "20")),
        plugin_timeout_seconds=float(os.getenv("JARVIS_PLUGIN_TIMEOUT_SECONDS", "5")),
        request_rate_limit_per_minute=int(os.getenv("JARVIS_REQUEST_RATE_LIMIT_PER_MINUTE", "120")),
        cloud_rate_limit_per_minute=int(os.getenv("JARVIS_CLOUD_RATE_LIMIT_PER_MINUTE", "30")),
        automation_rate_limit_per_minute=int(os.getenv("JARVIS_AUTOMATION_RATE_LIMIT_PER_MINUTE", "60")),
        plugin_rate_limit_per_minute=int(os.getenv("JARVIS_PLUGIN_RATE_LIMIT_PER_MINUTE", "60")),
        cloud_failure_threshold=int(os.getenv("JARVIS_CLOUD_FAILURE_THRESHOLD", "3")),
        cloud_cooldown_seconds=float(os.getenv("JARVIS_CLOUD_COOLDOWN_SECONDS", "30")),
        cloud_provider=os.getenv("JARVIS_CLOUD_PROVIDER", "openai"),
    )
    cfg.validate()
    return cfg
