from jarvis_assistant.plugins.base import PluginBase, PluginMetadata


class WeatherPlugin(PluginBase):
    metadata = PluginMetadata(name="weather", version="1.0.0", description="Weather lookups")

    def initialize(self) -> None:
        pass

    def can_handle(self, command: str) -> bool:
        return "weather" in command.lower()

    def handle(self, command: str, context: dict) -> dict:
        return {"success": True, "message": f"Weather plugin received: {command}"}


PLUGIN = WeatherPlugin()
