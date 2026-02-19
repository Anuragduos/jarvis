from __future__ import annotations

from jarvis_assistant.core.config import AppConfig
from jarvis_assistant.core.container import ServiceContainer


def run_cli_loop() -> None:
    config = AppConfig()
    assistant = ServiceContainer(config).build_assistant()

    print("JARVIS hybrid assistant (CLI mode). Type 'exit' to quit.")
    while True:
        text = input("You> ").strip()
        if text in {"exit", "quit"}:
            break
        response = assistant.handle_text(text)
        print(f"Jarvis> {response.text} [{response.metadata}]")


if __name__ == "__main__":
    run_cli_loop()
