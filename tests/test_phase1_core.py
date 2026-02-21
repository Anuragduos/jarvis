from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import pytest

from jarvis_assistant.contracts.results import ActionResult, ResultStatus
from jarvis_assistant.core.config import AppConfig
from jarvis_assistant.infrastructure.errors import ErrorBoundary
from jarvis_assistant.plugins.loader import PluginLoader
from jarvis_assistant.runtime.worker_pool import AsyncWorkerPool, WorkerTask


def test_error_boundary_contains_crash() -> None:
    boundary = ErrorBoundary(logging.getLogger("test"))

    def boom() -> int:
        raise ValueError("bad")

    result = boundary.safe_call(boom, fallback=lambda err: err.message)
    assert result == "bad"


def test_worker_pool_cpu_and_io() -> None:
    pool = AsyncWorkerPool(max_workers=2)

    async def run() -> None:
        cpu = await pool.run_cpu(lambda x: x + 1, 2)
        io = await pool.run_io(asyncio.sleep(0.01, result="ok"))
        pool.enqueue(WorkerTask(name="inc", func=lambda x: x + 1, args=(3,)))
        queued = pool.drain_once(timeout=1)
        assert (cpu, io, queued) == (3, "ok", 4)

    try:
        asyncio.run(run())
    finally:
        pool.shutdown()


def test_config_validation_error() -> None:
    with pytest.raises(Exception):
        AppConfig(max_workers=0).validate()


def test_plugin_loader_sandbox_on_failure(tmp_path: Path) -> None:
    plugin_file = tmp_path / "bad_plugin.py"
    plugin_file.write_text(
        """
from jarvis_assistant.plugins.base import PluginBase, PluginMetadata
class Bad(PluginBase):
    metadata = PluginMetadata(name='bad', version='1', description='bad')
    def initialize(self):
        raise RuntimeError('boom')
    def can_handle(self, command: str) -> bool:
        return False
    def handle(self, command: str, context: dict) -> dict:
        return {}
PLUGIN = Bad()
"""
    )
    loader = PluginLoader(tmp_path, ErrorBoundary(logging.getLogger("test")), logging.getLogger("test"))
    plugins = loader.load()
    assert plugins == []


def test_structured_action_result() -> None:
    result = ActionResult(status=ResultStatus.SUCCESS, confidence=0.9, message="ok")
    assert result.status == ResultStatus.SUCCESS
