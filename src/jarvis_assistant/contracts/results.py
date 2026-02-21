from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ResultStatus(str, Enum):
    """Standard status values for service responses."""

    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass(slots=True)
class ErrorInfo:
    """Structured error information."""

    code: str
    message: str
    recoverable: bool = True
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ActionResult:
    """Result for action execution calls."""

    status: ResultStatus
    confidence: float
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)
    error: ErrorInfo | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))


@dataclass(slots=True)
class ReasoningResult:
    """Result for reasoning and planning calls."""

    status: ResultStatus
    confidence: float
    plan_name: str
    steps: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    error: ErrorInfo | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))


@dataclass(slots=True)
class ExecutionReport:
    """Aggregated execution report for request lifecycle."""

    status: ResultStatus
    confidence: float
    correlation_id: str
    route: str
    metadata: dict[str, Any] = field(default_factory=dict)
    error: ErrorInfo | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    finished_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))


@dataclass(slots=True)
class DiagnosticReport:
    """Structured diagnostics report."""

    status: ResultStatus
    confidence: float
    checks: dict[str, bool]
    metadata: dict[str, Any] = field(default_factory=dict)
    error: ErrorInfo | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
