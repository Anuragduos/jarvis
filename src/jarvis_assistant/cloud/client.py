from __future__ import annotations

import asyncio
from dataclasses import dataclass

from jarvis_assistant.infrastructure.rate_limiter import SlidingWindowLimiter


@dataclass(slots=True)
class CloudResponse:
    """Cloud completion response model."""

    text: str
    cost_usd: float


class CloudClient:
    """Async cloud client with timeout, rate limiting, and cost estimation."""

    def __init__(self, timeout_seconds: float, max_per_minute: int = 30) -> None:
        self.timeout_seconds = timeout_seconds
        self.limiter = SlidingWindowLimiter(max_per_minute, 60.0)
        self.total_cost_usd = 0.0

    async def complete(self, prompt: str, provider: str) -> CloudResponse:
        """Executes async cloud completion call with timeout and quota checks."""

        if not self.limiter.allow():
            raise RuntimeError("Cloud request limit exceeded.")
        response = await asyncio.wait_for(self._simulate_request(prompt, provider), timeout=self.timeout_seconds)
        self.total_cost_usd += response.cost_usd
        return response

    async def _simulate_request(self, prompt: str, provider: str) -> CloudResponse:
        await asyncio.sleep(0.05)
        token_estimate = max(1, len(prompt.split()))
        cost = token_estimate * 0.00001
        return CloudResponse(text=f"[Cloud:{provider}] {prompt}", cost_usd=cost)

    async def stream_complete(self, prompt: str, provider: str) -> list[str]:
        """Returns streaming chunks for a completion."""

        full = await self.complete(prompt, provider)
        words = full.text.split()
        return [" ".join(words[: i + 1]) for i in range(len(words))]
