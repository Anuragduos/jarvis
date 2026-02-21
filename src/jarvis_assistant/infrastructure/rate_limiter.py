from __future__ import annotations

import time
from collections import deque


class SlidingWindowLimiter:
    """Sliding-window limiter for abuse protection."""

    def __init__(self, limit: int, window_seconds: float) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: deque[float] = deque()

    def allow(self) -> bool:
        """Returns whether a new event is allowed."""

        now = time.time()
        while self._events and now - self._events[0] > self.window_seconds:
            self._events.popleft()
        if len(self._events) >= self.limit:
            return False
        self._events.append(now)
        return True

    def remaining(self) -> int:
        """Returns remaining budget for current window."""

        now = time.time()
        while self._events and now - self._events[0] > self.window_seconds:
            self._events.popleft()
        return max(0, self.limit - len(self._events))
