from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import AssistantMode


@dataclass
class SecurityConfig:
    require_confirmation_for_dangerous: bool = True
    encrypted_key_file: Path = Path(".secrets/api_keys.enc")
    keyring_file: Path = Path(".secrets/master.key")


@dataclass
class MemoryConfig:
    sqlite_path: Path = Path("data/memory.db")
    faiss_index_path: Path = Path("data/memory.index")


@dataclass
class ModelConfig:
    local_stt: str = "whisper"
    local_llm_model: str = "mistral:7b-instruct"
    cloud_provider: str = "openai"
    intent_model_path: Path = Path("models/intent_classifier.pt")


@dataclass
class UIConfig:
    theme: str = "dark"
    personality: float = 0.5


@dataclass
class AppConfig:
    mode: AssistantMode = AssistantMode.HYBRID
    security: SecurityConfig = field(default_factory=SecurityConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    ui: UIConfig = field(default_factory=UIConfig)
