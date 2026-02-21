from __future__ import annotations

import asyncio

from jarvis_assistant.core.config import AppConfig
from jarvis_assistant.core.container import ServiceContainer


def test_assistant_handles_executor_crash() -> None:
    container = ServiceContainer(AppConfig())
    assistant = container.build_assistant()

    def crash(_plan):
        raise RuntimeError("executor boom")

    assistant.executor.execute_plan = crash  # type: ignore[method-assign]
    response = asyncio.run(assistant.handle_text("open calculator"))
    assert response.executed is False
    assert response.metadata["status"] in {"failed", "timeout", "cancelled"}
    container.shutdown()
