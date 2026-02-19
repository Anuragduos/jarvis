from __future__ import annotations

import os
import shutil
from dataclasses import dataclass


@dataclass(slots=True)
class HardwareProfile:
    """Host hardware profile used for runtime scaling."""

    cpu_cores: int
    ram_gb: float
    disk_free_gb: float
    has_gpu: bool


class HardwareProfiler:
    """Collects hardware facts for auto-scaling decisions."""

    def profile(self) -> HardwareProfile:
        """Returns current host hardware profile."""

        cpu_cores = os.cpu_count() or 2
        ram_gb = self._ram_gb()
        disk_free_gb = shutil.disk_usage(".").free / (1024**3)
        has_gpu = False
        try:
            import torch

            has_gpu = bool(torch.cuda.is_available())
        except Exception:  # noqa: BLE001
            has_gpu = False
        return HardwareProfile(cpu_cores=cpu_cores, ram_gb=ram_gb, disk_free_gb=disk_free_gb, has_gpu=has_gpu)

    def _ram_gb(self) -> float:
        try:
            import psutil

            return psutil.virtual_memory().total / (1024**3)
        except Exception:  # noqa: BLE001
            pages = os.sysconf("SC_PHYS_PAGES")
            page_size = os.sysconf("SC_PAGE_SIZE")
            return (pages * page_size) / (1024**3)

    def recommended_workers(self, profile: HardwareProfile) -> int:
        """Returns safe worker count recommendation."""

        if profile.ram_gb < 4:
            return max(1, min(2, profile.cpu_cores // 2))
        return max(2, min(16, profile.cpu_cores))

    def recommended_model_tier(self, profile: HardwareProfile) -> str:
        """Returns local model size tier based on RAM."""

        if profile.ram_gb < 8:
            return "small"
        if profile.ram_gb < 16:
            return "medium"
        return "large"
