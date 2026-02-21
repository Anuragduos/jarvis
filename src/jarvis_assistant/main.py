from __future__ import annotations

import asyncio

from jarvis_assistant.core.config import load_config
from jarvis_assistant.core.container import ServiceContainer


async def run_cli_loop() -> None:
    """CLI entrypoint for development usage."""

    config = load_config()
    container = ServiceContainer(config)
    assistant = container.build_assistant()

    diagnostic = container.diagnostics.run()
    print(f"Diagnostics: {diagnostic.status.value} {diagnostic.checks}")

    print("JARVIS hybrid assistant (CLI mode). Type 'exit' to quit.")
    try:
        while True:
            text = input("You> ").strip()
            if text in {"exit", "quit"}:
                break
            response = await assistant.handle_text(text)
            print(f"Jarvis> {response.text} [{response.metadata}]")
    finally:
        container.shutdown()


if __name__ == "__main__":
    asyncio.run(run_cli_loop())
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
