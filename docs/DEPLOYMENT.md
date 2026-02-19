# Deployment Guide

## 1) Local Development
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
python -m jarvis_assistant.main
```

## 2) Run UI
```bash
export PYTHONPATH=src
python -m jarvis_assistant.ui.app
```

## 3) Optional Offline Model Stack
- Install Ollama and pull model:
  - `ollama pull mistral:7b-instruct`
- Install local STT model assets for Whisper/Vosk.

## 4) Configure Online Providers
Set secure API keys via encrypted vault (or env injection):
- `OPENAI_API_KEY`
- `GROQ_API_KEY`
- `HF_TOKEN`

## 5) Packaging
```bash
pip install pyinstaller
pyinstaller --name jarvis --onefile src/jarvis_assistant/main.py
```

## 6) Operational Recommendations
- Run automation tasks with least-privilege OS account.
- Enable command audit log retention.
- Keep plugin folder signed/controlled in production.
