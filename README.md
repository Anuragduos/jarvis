# JARVIS Hybrid AI Platform (Production Upgrade)

This repository is being upgraded in controlled phases.

## Upgraded Target Architecture

```text
src/jarvis_assistant/
├── ai/
├── automation/
├── cloud/
├── contracts/
│   └── results.py
├── core/
│   ├── assistant.py
│   ├── config.py
│   ├── container.py
│   └── decision_engine.py
├── infrastructure/
│   ├── errors.py
│   └── logging.py
├── memory/
├── plugins/
├── runtime/
│   └── worker_pool.py
├── security/
├── transactions/
│   └── undo.py
├── ui/
└── utils/
```

## Phase 1 (Implemented)
- Centralized structured logging with correlation IDs and timing.
- Error boundaries with crash containment and safe fallback objects.
- Async worker pool (CPU thread pool + asyncio loop + queue + shutdown).
- Validated configuration loading from environment with startup checks.
- Structured result contracts: `ActionResult`, `ReasoningResult`, `ExecutionReport`, `DiagnosticReport`.
- Undo/transaction journal with soft-delete + rollback hooks.
- Expanded tests for worker, config validation, plugin sandboxing, and failure injection.

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
pytest -q
python -m jarvis_assistant.main
```
