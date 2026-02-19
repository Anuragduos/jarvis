# Implementation Plan (Production Track)

## Phase 1: Foundation
- Establish layered modules and interfaces.
- Implement DI container and configuration system.
- Set up SQLite memory and base command log.

## Phase 2: Offline Intelligence
- Integrate Whisper/Vosk local STT.
- Add spaCy+NLTK preprocessing pipeline.
- Train and evaluate PyTorch intent classifier.
- Add Ollama adapter for local reasoning.

## Phase 3: Online Intelligence
- Add cloud provider adapters (OpenAI/Groq/HF).
- Add real-time data services (weather/news/stocks).
- Implement model router with confidence + sensitivity gating.

## Phase 4: Automation + Safety
- Expand automation actions (filesystem, browser, email drafting).
- Add dangerous-action confirmation dialogs.
- Introduce undo transaction journal where possible.

## Phase 5: UX & Control
- Finalize PyQt6 animated orb states.
- Add status events, command console, settings panel.
- Add debug console and self-diagnostics panel.

## Phase 6: Learning & Personalization
- FAISS semantic memory integration.
- Preference learning and command pattern learning.
- Emotional tone and adaptive personality tuning.

## Phase 7: Scale & Hardening
- Multi-thread workers and async cloud execution.
- Hardware-aware model/threads selection.
- Add test coverage, packaging, and observability.
