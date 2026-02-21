from __future__ import annotations

import contextlib
import contextvars
import logging
import time
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Iterator


_correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar("correlation_id", default="-")


class CorrelationFilter(logging.Filter):
    """Injects correlation ID into every log entry."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = _correlation_id.get()
        return True


class StructuredLoggerFactory:
    """Creates application loggers with console and rotating file handlers."""

    def __init__(self, log_path: Path = Path("logs/jarvis.log"), level: int = logging.INFO) -> None:
        self.log_path = log_path
        self.level = level
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def build(self, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        if logger.handlers:
            return logger

        logger.setLevel(self.level)
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] [cid=%(correlation_id)s] %(message)s"
        )

        file_handler = RotatingFileHandler(self.log_path, maxBytes=2_000_000, backupCount=5)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(CorrelationFilter())

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.addFilter(CorrelationFilter())

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.propagate = False
        return logger


def new_correlation_id() -> str:
    """Creates and sets a correlation ID for current context."""

    cid = str(uuid.uuid4())
    _correlation_id.set(cid)
    return cid


def current_correlation_id() -> str:
    """Returns current correlation ID."""

    return _correlation_id.get()


@contextlib.contextmanager
def timed_operation(logger: logging.Logger, operation_name: str) -> Iterator[None]:
    """Context manager for performance timing logs."""

    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("operation=%s elapsed_ms=%.2f", operation_name, elapsed_ms)
