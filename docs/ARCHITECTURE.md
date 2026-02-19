# Hybrid J.A.R.V.I.S.-Style Assistant Architecture

This project implements a **modular hybrid AI assistant** with seamless offline/online execution, production-oriented interfaces, and layered separation of concerns.

## Layered System Design

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                            UI LAYER (PyQt6)                             │
│   OrbWidget + Console + Settings + Diagnostic Panel                     │
└──────────────────────────────────────────────────────────────────────────┘
                 │ events/status                                ▲ responses
                 ▼                                              │
┌──────────────────────────────────────────────────────────────────────────┐
│                   VOICE INTERFACE LAYER                                 │
│  STT Adapter (Vosk/Whisper local) + TTS Adapter + Wakeword             │
└──────────────────────────────────────────────────────────────────────────┘
                 │ text/audio                                     ▲ speech
                 ▼                                                 │
┌──────────────────────────────────────────────────────────────────────────┐
│                 NLP + INTENT ENGINE LAYER                               │
│  spaCy entity extraction + NLTK preprocessing + IntentClassifier        │
│  + rule parser fallback + confidence scorer                             │
└──────────────────────────────────────────────────────────────────────────┘
                 │ intents/entities/tasks                         ▲ context
                 ▼                                                │
┌──────────────────────────────────────────────────────────────────────────┐
│              NEURAL REASONING & PLANNING LAYER                          │
│  Local LLM adapter (Ollama) + cloud LLM router + task planner           │
│  emotional tone + adaptive personality engine                            │
└──────────────────────────────────────────────────────────────────────────┘
                 │ action plans                                   ▲ results
                 ▼                                                 │
┌──────────────────────────────────────────────────────────────────────────┐
│               TASK EXECUTION & AUTOMATION LAYER                         │
│ pyautogui/os/subprocess/psutil/Selenium + scheduler + macro engine      │
└──────────────────────────────────────────────────────────────────────────┘
                 │ reads/writes                                   ▲ logs
                 ▼                                                 │
┌──────────────────────────────────────────────────────────────────────────┐
│               MEMORY & CONTEXT SYSTEM                                   │
│ SQLite structured memory + FAISS semantic memory + preferences          │
└──────────────────────────────────────────────────────────────────────────┘
                 │ providers                                       ▲ telemetry
                 ▼                                                 │
┌──────────────────────────────────────────────────────────────────────────┐
│                  CLOUD INTEGRATION LAYER                                │
│ OpenAI/Groq/HF + weather/news/stocks + web search adapters             │
└──────────────────────────────────────────────────────────────────────────┘

Cross-cutting: Security/Permission Layer + Plugin System + Diagnostics.
```

## Dependency Injection Principles

- Each service implements a protocol-like interface.
- `ServiceContainer` wires dependencies in one place.
- Higher layers depend on abstractions (interfaces) rather than concrete providers.
- Providers are swappable via config and mode flags.

## Hybrid Decision Engine

1. **Sensitive** tasks -> force local execution.
2. **Simple** tasks (confidence high, known intent) -> local only.
3. **Complex reasoning** (multi-hop, low confidence, broad knowledge) -> cloud fallback.
4. User can override globally: `OFFLINE`, `ONLINE`, `HYBRID`.

## Threading & Runtime

- UI thread: rendering and user interaction.
- Worker pool: NLP, reasoning, automation.
- Dedicated I/O async workers for cloud calls.
- Optional GPU acceleration for Whisper/PyTorch/LLM where available.

## Security & Safeguards

- Permission policy checks before action execution.
- Dangerous actions require explicit confirmation.
- Command logging and undo transaction record (best-effort).
- Encrypted API key vault (Fernet over local file).

## Plugin Model

- `plugins/` contains Python modules implementing `PluginBase`.
- Dynamic import + lifecycle hooks (`initialize`, `can_handle`, `handle`).
- Plugin manifest metadata supports capability discovery.

## Diagnostics & Scaling

- Self-diagnostics checks: microphone, model availability, DB integrity, plugin validity.
- Hardware profiler determines local model size and thread counts.
