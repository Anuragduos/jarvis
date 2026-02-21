from __future__ import annotations

import logging

from jarvis_assistant.cloud.client import CloudClient
from jarvis_assistant.core.config import AppConfig
from jarvis_assistant.infrastructure.circuit_breaker import CircuitBreaker


class ModelRouter:
    """Async model routing with cloud failover protections."""

    def __init__(self, config: AppConfig, circuit_breaker: CircuitBreaker, logger: logging.Logger) -> None:
        self.config = config
        self.circuit_breaker = circuit_breaker
        self.logger = logger
        self.cloud_client = CloudClient(
            timeout_seconds=config.request_timeout_seconds,
            max_per_minute=config.cloud_rate_limit_per_minute,
        )

    async def generate(self, text: str, route: str) -> str:
        """Generates text from selected route with circuit handling."""

        if route == "local":
            return self._local_generate(text)
        if not self.circuit_breaker.allow_request():
            self.logger.warning("cloud_blocked_by_circuit")
            return self._local_generate(text)
        try:
            response = await self.cloud_client.complete(text, provider=self.config.cloud_provider)
            self.circuit_breaker.record_success()
            self.logger.info("cloud_cost_total_usd=%.6f", self.cloud_client.total_cost_usd)
            return response.text
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("cloud_call_failed error=%s", exc)
            self.circuit_breaker.record_failure()
            return self._local_generate(text)

    async def stream_generate(self, text: str, route: str) -> list[str]:
        """Generates streaming chunks for response text."""

        if route == "local":
            full = self._local_generate(text)
            words = full.split()
            return [" ".join(words[: i + 1]) for i in range(len(words))]
        try:
            return await self.cloud_client.stream_complete(text, provider=self.config.cloud_provider)
        except Exception:  # noqa: BLE001
            full = self._local_generate(text)
            words = full.split()
            return [" ".join(words[: i + 1]) for i in range(len(words))]

    def _local_generate(self, text: str) -> str:
        return f"[Local reasoning] {text}"
from jarvis_assistant.core.config import ModelConfig


class ModelRouter:
    def __init__(self, config: ModelConfig) -> None:
        self.config = config

    def generate(self, text: str, route: str) -> str:
        if route == "local":
            return self._local_generate(text)
        return self._cloud_generate(text)

    def _local_generate(self, text: str) -> str:
        # Integrate with Ollama in production.
        return f"[Local reasoning] {text}"

    def _cloud_generate(self, text: str) -> str:
        # Integrate with OpenAI/Groq/HF in production.
        provider = self.config.cloud_provider
        return f"[Cloud:{provider}] {text}"
