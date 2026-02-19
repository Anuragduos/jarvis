from __future__ import annotations

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
