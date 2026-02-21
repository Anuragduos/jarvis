from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass(slots=True)
class CircuitState:
    """Public circuit breaker state snapshot."""

    is_open: bool
    failure_count: int
    opened_until: float | None


class CircuitBreaker:
    """Simple circuit breaker for cloud reliability."""

    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 30.0) -> None:
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self._failure_count = 0
        self._opened_until: float | None = None

    def allow_request(self) -> bool:
        """Returns whether cloud requests are currently allowed."""

        if self._opened_until is None:
            return True
        if time.time() >= self._opened_until:
            self._opened_until = None
            self._failure_count = 0
            return True
        return False

    def record_success(self) -> None:
        """Resets breaker failure counters after successful call."""

        self._failure_count = 0
        self._opened_until = None

    def record_failure(self) -> None:
        """Records call failure and opens circuit on threshold."""

        self._failure_count += 1
        if self._failure_count >= self.failure_threshold:
            self._opened_until = time.time() + self.cooldown_seconds

    def state(self) -> CircuitState:
        """Returns current breaker state."""

        return CircuitState(
            is_open=not self.allow_request(),
            failure_count=self._failure_count,
            opened_until=self._opened_until,
        )
