from __future__ import annotations

import asyncio

from jarvis_assistant.cloud.model_router import ModelRouter
from jarvis_assistant.core.config import AppConfig
from jarvis_assistant.infrastructure.circuit_breaker import CircuitBreaker


def test_circuit_breaker_fallback_to_local() -> None:
    config = AppConfig(cloud_failure_threshold=1)
    circuit = CircuitBreaker(failure_threshold=1, cooldown_seconds=60)
    router = ModelRouter(config=config, circuit_breaker=circuit, logger=__import__("logging").getLogger("test"))
    circuit.record_failure()
    output = asyncio.run(router.generate("hello", route="cloud"))
    assert output.startswith("[Local reasoning]")


def test_streaming_response_chunks() -> None:
    config = AppConfig()
    circuit = CircuitBreaker()
    router = ModelRouter(config=config, circuit_breaker=circuit, logger=__import__("logging").getLogger("test"))
    chunks = asyncio.run(router.stream_generate("hello world", route="local"))
    assert len(chunks) >= 2
