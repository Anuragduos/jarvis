from __future__ import annotations

import asyncio
import concurrent.futures
import queue
import threading
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class WorkerTask:
    """Queued task representation."""

    name: str
    func: Callable[..., Any]
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] | None = None


class AsyncWorkerPool:
    """Hybrid worker pool for CPU and async I/O tasks with graceful shutdown."""

    def __init__(self, max_workers: int = 4) -> None:
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(target=self._run_loop, daemon=True)
        self._loop_thread.start()
        self.queue: queue.Queue[WorkerTask] = queue.Queue()
        self._shutdown = threading.Event()

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def run_cpu(self, fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Runs CPU-bound work in thread pool."""

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, lambda: fn(*args, **kwargs))

    async def run_io(self, coro: Coroutine[Any, Any, T]) -> T:
        """Runs async I/O coroutine on dedicated loop."""

        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, future.result)

    def submit_cpu(self, fn: Callable[..., T], *args: Any, timeout: float | None = None, **kwargs: Any) -> T:
        future = self.executor.submit(fn, *args, **kwargs)
        return future.result(timeout=timeout)

    def submit_io(self, coro: asyncio.Future[T] | Coroutine[Any, Any, T], timeout: float | None = None) -> T:
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result(timeout=timeout)

    def enqueue(self, task: WorkerTask) -> None:
        self.queue.put(task)

    def drain_once(self, timeout: float | None = None) -> Any:
        task = self.queue.get(timeout=timeout)
        kwargs = task.kwargs or {}
        return self.submit_cpu(task.func, *task.args, **kwargs)

    def shutdown(self) -> None:
        if self._shutdown.is_set():
            return
        self._shutdown.set()
        self.executor.shutdown(wait=True, cancel_futures=True)
        self.loop.call_soon_threadsafe(self.loop.stop)
        self._loop_thread.join(timeout=2)
