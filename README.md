# JARVIS Hybrid Assistant (Offline + Online)

A modular AI assistant architecture inspired by J.A.R.V.I.S., with seamless local/cloud intelligence routing, desktop automation, persistent memory, and a futuristic PyQt6 orb UI.

## Key Features
- Hybrid execution modes: **Offline**, **Online**, and **Hybrid auto-routing**.
- Local stack: Whisper/Vosk STT, NLP preprocessing, PyTorch intent model, SQLite memory.
- Cloud stack: OpenAI/Groq/HuggingFace-ready adapters and real-time data providers.
- Automation engine with logging, confirmations, and undo placeholders.
- Extensible plugin framework with dynamic loading.
- Animated Siri-like orb UI built with PyQt6.

## Folder Structure

```text
.
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   └── IMPLEMENTATION_PLAN.md
├── plugins/
│   ├── developer_tools_plugin.py
│   ├── smart_reminders_plugin.py
│   ├── system_monitor_plugin.py
│   └── weather_plugin.py
├── src/jarvis_assistant/
│   ├── ai/
│   │   ├── emotion.py
│   │   ├── intent_model.py
│   │   ├── nlp_engine.py
│   │   └── reasoning.py
│   ├── automation/
│   │   └── executor.py
│   ├── cloud/
│   │   ├── model_router.py
│   │   └── realtime_data.py
│   ├── core/
│   │   ├── assistant.py
│   │   ├── config.py
│   │   ├── container.py
│   │   ├── decision_engine.py
│   │   ├── models.py
│   │   └── voice.py
│   ├── memory/
│   │   ├── context_manager.py
│   │   ├── store.py
│   │   └── vector_store.py
│   ├── plugins/
│   │   ├── base.py
│   │   └── loader.py
│   ├── security/
│   │   ├── permissions.py
│   │   └── vault.py
│   ├── ui/
│   │   ├── app.py
│   │   ├── main_window.py
│   │   └── orb_widget.py
│   ├── utils/
│   │   └── diagnostics.py
│   └── main.py
└── requirements.txt
```

## Mode Switching Logic

`ModeDecisionEngine` routes requests using policy:
1. Manual offline mode -> local.
2. Manual online mode -> cloud unless sensitive.
3. Sensitive tasks -> local-only.
4. Simple/high-confidence tasks -> local.
5. Complex/low-confidence tasks -> cloud fallback.

See: `src/jarvis_assistant/core/decision_engine.py`

## Quick Start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
python -m jarvis_assistant.main
```

Run UI:
```bash
export PYTHONPATH=src
python -m jarvis_assistant.ui.app
```

## Production Notes
- Connect STT adapters in `core/voice.py`.
- Replace stub model calls in `cloud/model_router.py`.
- Harden automation commands before broad OS deployment.
- Add plugin signing and secure distribution.
