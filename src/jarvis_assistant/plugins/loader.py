from __future__ import annotations

import importlib.util
from pathlib import Path

from .base import PluginBase


class PluginLoader:
    def __init__(self, plugin_dir: Path) -> None:
        self.plugin_dir = plugin_dir
        self.plugins: list[PluginBase] = []

    def load(self) -> list[PluginBase]:
        self.plugins.clear()
        for path in self.plugin_dir.glob("*.py"):
            if path.name.startswith("_"):
                continue
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
