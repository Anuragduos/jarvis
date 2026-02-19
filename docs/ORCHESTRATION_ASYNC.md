# Async Orchestration Flow (Updated)

```text
UI/CLI Event Loop
   │
   ▼
JarvisAssistant.handle_text(text) [async]
   │  (request limiter + correlation id)
   ├─▶ worker_pool.run_cpu(NLP.parse)
   ├─▶ tone_detector.detect + urgency/stress
   ├─▶ worker_pool.run_cpu(Reasoning.estimate_complexity)
   ├─▶ DecisionEngine.decide(..., circuit_state)
   ├─▶ await ReasoningEngine.create_plan(...)
   │      └─▶ await ModelRouter.generate(...)
   │             ├─ local route (fast local)
   │             └─ cloud route (CloudClient async + timeout + rate limit + circuit breaker)
   ├─▶ worker_pool.run_cpu(AutomationExecutor.execute_plan)
   │      ├─ system action with permission checks
   │      └─ plugin action with registry lookup + policy + timeout + crash boundary
   ├─▶ personality.apply_style(response, tone)
   ├─▶ context_manager.record_interaction(...)
   └─▶ return AssistantResponse(metadata includes route, trace, metrics, circuit state)

All external/slow operations run with timeout guards.
No blocking calls on UI thread.
```
