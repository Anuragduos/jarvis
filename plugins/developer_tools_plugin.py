import subprocess

from jarvis_assistant.plugins.base import PluginBase, PluginMetadata


class DeveloperToolsPlugin(PluginBase):
    metadata = PluginMetadata(name="developer_tools", version="1.0.0", description="Run safe dev commands")

    def initialize(self) -> None:
        self.allowed_prefixes = ("python", "pytest", "ruff", "git status")

    def can_handle(self, command: str) -> bool:
        return command.lower().startswith("dev:")

    def handle(self, command: str, context: dict) -> dict:
        del context
        cmd = command.replace("dev:", "", 1).strip()
        if not cmd.startswith(self.allowed_prefixes):
            return {"success": False, "message": "Command blocked by policy."}
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
        return {"success": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr}


PLUGIN = DeveloperToolsPlugin()
