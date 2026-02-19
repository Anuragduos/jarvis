from __future__ import annotations

import asyncio

from jarvis_assistant.core.config import AppConfig
from jarvis_assistant.core.container import ServiceContainer


def test_async_handle_text_and_tone_metadata() -> None:
    container = ServiceContainer(AppConfig())
    assistant = container.build_assistant()
    response = asyncio.run(assistant.handle_text("thanks, please remind me now"))
    assert "tone" in response.metadata
    assert "urgent" in response.metadata
    container.shutdown()


def test_plugin_execution_pipeline() -> None:
    container = ServiceContainer(AppConfig())
    assistant = container.build_assistant()
    response = asyncio.run(assistant.handle_text("remind me to deploy at 5"))
    assert response.metadata["status"] in {"success", "failed"}
    container.shutdown()
