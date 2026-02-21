from __future__ import annotations

import logging
from collections.abc import Callable
from typing import ParamSpec, TypeVar

from jarvis_assistant.contracts.results import ErrorInfo

P = ParamSpec("P")
T = TypeVar("T")


class ErrorBoundary:
    """Contains crashes and returns structured error responses."""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def safe_call(
        self,
        fn: Callable[P, T],
        *args: P.args,
        fallback: Callable[[ErrorInfo], T],
        **kwargs: P.kwargs,
    ) -> T:
        """Executes callable safely and uses fallback on exception."""

        try:
            return fn(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            info = ErrorInfo(
                code=exc.__class__.__name__,
                message=str(exc),
                recoverable=True,
            )
            self.logger.exception("service_crash_contained error=%s", info.code)
            return fallback(info)
