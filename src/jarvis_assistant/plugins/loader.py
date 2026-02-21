from __future__ import annotations

import importlib.util
import logging
from pathlib import Path

from jarvis_assistant.contracts.results import ErrorInfo
from jarvis_assistant.infrastructure.errors import ErrorBoundary

from pathlib import Path

from .base import PluginBase


class PluginLoader:
    """Dynamic plugin loader with crash containment."""

    def __init__(self, plugin_dir: Path, error_boundary: ErrorBoundary, logger: logging.Logger) -> None:
        self.plugin_dir = plugin_dir
        self.error_boundary = error_boundary
        self.logger = logger
        self.plugins: list[PluginBase] = []

    def load(self) -> list[PluginBase]:
        """Loads plugins from folder and initializes safely."""

    def __init__(self, plugin_dir: Path) -> None:
        self.plugin_dir = plugin_dir
        self.plugins: list[PluginBase] = []

    def load(self) -> list[PluginBase]:
        self.plugins.clear()
        for path in self.plugin_dir.glob("*.py"):
            if path.name.startswith("_"):
                continue
            plugin = self._load_single(path)
            if plugin is not None:
                self.plugins.append(plugin)
        return self.plugins

    def _load_single(self, path: Path) -> PluginBase | None:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)

        failed = False

        def import_module() -> bool:
            spec.loader.exec_module(module)
            return True

        def import_fallback(_: ErrorInfo) -> bool:
            nonlocal failed
            failed = True
            return False

        self.error_boundary.safe_call(import_module, fallback=import_fallback)
        if failed:
            self.logger.warning("plugin_import_failed plugin=%s", path.name)
            return None

        plugin = getattr(module, "PLUGIN", None)
        if plugin is None:
            return None

        init_failed = False

        def init_call() -> bool:
            plugin.initialize()
            return True

        def init_fallback(_: ErrorInfo) -> bool:
            nonlocal init_failed
            init_failed = True
            return False

        self.error_boundary.safe_call(init_call, fallback=init_fallback)
        if init_failed:
            self.logger.warning("plugin_initialization_failed plugin=%s", path.name)
            return None

        self.logger.info("plugin_loaded plugin=%s", path.name)
        return plugin
            spec = importlib.util.spec_from_file_location(path.stem, path)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            plugin = getattr(module, "PLUGIN", None)
            if plugin:
                plugin.initialize()
                self.plugins.append(plugin)
        return self.plugins
