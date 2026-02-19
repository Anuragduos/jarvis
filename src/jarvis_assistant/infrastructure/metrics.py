from __future__ import annotations

import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator


@dataclass(slots=True)
class MetricPoint:
    """Simple metric aggregation point."""

    count: int = 0
    total_ms: float = 0.0


class MetricsCollector:
    """Collects per-layer latency metrics."""

    def __init__(self) -> None:
        self._points: dict[str, MetricPoint] = defaultdict(MetricPoint)

    @contextmanager
    def time_block(self, name: str) -> Iterator[None]:
        """Tracks elapsed latency for named block."""

        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            point = self._points[name]
            point.count += 1
            point.total_ms += elapsed_ms

    def snapshot(self) -> dict[str, dict[str, float]]:
        """Returns summarized metrics snapshot."""

        out: dict[str, dict[str, float]] = {}
        for name, point in self._points.items():
            avg = point.total_ms / point.count if point.count else 0.0
            out[name] = {"count": float(point.count), "total_ms": point.total_ms, "avg_ms": avg}
        return out
