import psutil

from jarvis_assistant.plugins.base import PluginBase, PluginMetadata


class SystemMonitorPlugin(PluginBase):
    metadata = PluginMetadata(name="system_monitor", version="1.0.0", description="CPU/RAM stats")

    def initialize(self) -> None:
        pass

    def can_handle(self, command: str) -> bool:
        return "system" in command.lower() or "cpu" in command.lower()

    def handle(self, command: str, context: dict) -> dict:
        del command, context
        return {
            "success": True,
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "ram_percent": psutil.virtual_memory().percent,
        }


PLUGIN = SystemMonitorPlugin()
