from __future__ import annotations

import shutil
from pathlib import Path


class SelfDiagnostics:
    def run(self) -> dict[str, bool]:
        return {
            "python_available": True,
            "ollama_installed": shutil.which("ollama") is not None,
            "plugins_dir_exists": Path("plugins").exists(),
            "data_dir_exists": Path("data").exists() or Path("data").mkdir(exist_ok=True) is None,
        }
