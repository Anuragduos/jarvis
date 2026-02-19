from datetime import datetime

from jarvis_assistant.plugins.base import PluginBase, PluginMetadata


class SmartRemindersPlugin(PluginBase):
    metadata = PluginMetadata(name="smart_reminders", version="1.0.0", description="Simple reminders")

    def initialize(self) -> None:
        self.reminders: list[dict] = []

    def can_handle(self, command: str) -> bool:
        return "remind" in command.lower() or "schedule" in command.lower()

    def handle(self, command: str, context: dict) -> dict:
        reminder = {"text": command, "created_at": datetime.utcnow().isoformat()}
        self.reminders.append(reminder)
        return {"success": True, "message": "Reminder saved.", "reminder": reminder}


PLUGIN = SmartRemindersPlugin()
