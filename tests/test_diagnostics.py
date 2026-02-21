from __future__ import annotations

import logging

from jarvis_assistant.core.config import AppConfig
from jarvis_assistant.infrastructure.hardware_profiler import HardwareProfile
from jarvis_assistant.utils.diagnostics import SelfDiagnostics


def test_diagnostics_report_structure() -> None:
    diag = SelfDiagnostics(
        config=AppConfig(),
        plugin_registry={"x": object()},
        hardware_profile=HardwareProfile(cpu_cores=4, ram_gb=8, disk_free_gb=10, has_gpu=False),
        logger=logging.getLogger("test"),
    )
    report = diag.run()
    assert "db_integrity" in report.checks
    assert report.confidence >= 0.0
