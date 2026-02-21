from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from jarvis_assistant.ai.emotion import AdaptivePersonality, EmotionalToneDetector
from jarvis_assistant.ai.nlp_engine import NLPEngine
from jarvis_assistant.ai.reasoning import ReasoningEngine
from jarvis_assistant.automation.executor import AutomationExecutor
from jarvis_assistant.contracts.results import ActionResult, ErrorInfo, ExecutionReport, ResultStatus
from jarvis_assistant.infrastructure.circuit_breaker import CircuitBreaker
from jarvis_assistant.infrastructure.errors import ErrorBoundary
from jarvis_assistant.infrastructure.logging import new_correlation_id, timed_operation
from jarvis_assistant.infrastructure.metrics import MetricsCollector
from jarvis_assistant.infrastructure.rate_limiter import SlidingWindowLimiter
from jarvis_assistant.memory.context_manager import ContextManager
from jarvis_assistant.runtime.worker_pool import AsyncWorkerPool
from jarvis_assistant.ai.nlp_engine import NLPEngine
from jarvis_assistant.ai.reasoning import ReasoningEngine
from jarvis_assistant.automation.executor import AutomationExecutor
from jarvis_assistant.memory.context_manager import ContextManager
from jarvis_assistant.security.permissions import PermissionManager

from .config import AppConfig
from .decision_engine import ModeDecisionEngine
from .models import AssistantResponse


class JarvisAssistant:
    """Coordinator service for one assistant request lifecycle."""

    def __init__(
        self,
        config: AppConfig,
        nlp: NLPEngine,
        reasoning: ReasoningEngine,
        executor: AutomationExecutor,
        context: ContextManager,
        permissions: PermissionManager,
        decision_engine: ModeDecisionEngine,
        error_boundary: ErrorBoundary,
        worker_pool: AsyncWorkerPool,
        circuit_breaker: CircuitBreaker,
        request_limiter: SlidingWindowLimiter,
        metrics: MetricsCollector,
        tone_detector: EmotionalToneDetector,
        personality: AdaptivePersonality,
        logger: logging.Logger,
    ) -> None:
        self.config = config
        self.nlp = nlp
        self.reasoning = reasoning
        self.executor = executor
        self.context = context
        self.permissions = permissions
        self.decision_engine = decision_engine
        self.error_boundary = error_boundary
        self.worker_pool = worker_pool
        self.circuit_breaker = circuit_breaker
        self.request_limiter = request_limiter
        self.metrics = metrics
        self.tone_detector = tone_detector
        self.personality = personality
        self.logger = logger

    async def handle_text(self, text: str) -> AssistantResponse:
        """Processes input text asynchronously without blocking UI thread."""

        if not self.request_limiter.allow():
            return AssistantResponse(
                text="Request limit exceeded. Please wait.",
                executed=False,
                metadata={"status": ResultStatus.FAILED.value, "code": "REQUEST_RATE_LIMIT"},
            )

        started_at = datetime.now(tz=timezone.utc)
        correlation_id = new_correlation_id()

        with timed_operation(self.logger, "handle_text"):
            intent = None
            decision_route = "local"
            decision_reason = "unavailable"
            tone = "neutral"
            tone_meta: dict[str, bool] = {"urgent": False, "stressed": False}
            try:
                with self.metrics.time_block("nlp.parse"):
                    intent = await asyncio.wait_for(
                        self.worker_pool.run_cpu(self.nlp.parse, text),
                        timeout=self.config.request_timeout_seconds,
                    )

                tone = self.tone_detector.detect(text)
                tone_meta = self.tone_detector.detect_urgency_and_stress(text)

                with self.metrics.time_block("reasoning.complexity"):
                    complexity = await asyncio.wait_for(
                        self.worker_pool.run_cpu(self.reasoning.estimate_complexity, text, intent),
                        timeout=self.config.request_timeout_seconds,
                    )

                decision = self.decision_engine.decide(
                    mode=self.config.execution_mode,
                    intent=intent,
                    is_sensitive=self.permissions.is_sensitive_intent(intent.intent),
                    complexity_score=complexity,
                    circuit_state=self.circuit_breaker.state(),
                )

                decision_route = decision.route
                decision_reason = decision.reason

                with self.metrics.time_block("reasoning.plan"):
                    reasoning_result = await asyncio.wait_for(
                        self.reasoning.create_plan(text=text, intent=intent, route=decision.route),
                        timeout=self.config.request_timeout_seconds,
                    )

                if reasoning_result.status != ResultStatus.SUCCESS:
                    report = ExecutionReport(
                        status=reasoning_result.status,
                        confidence=reasoning_result.confidence,
                        correlation_id=correlation_id,
                        route=decision_route,
                        error=reasoning_result.error,
                        metadata={"stage": "reasoning", "tone": tone, **tone_meta},
                        started_at=started_at,
                        finished_at=datetime.now(tz=timezone.utc),
                    )
                    return self._response_from_report(report)

                with self.metrics.time_block("executor.run"):
                    action_result = await asyncio.wait_for(
                        self.worker_pool.run_cpu(self.executor.execute_plan, reasoning_result),
                        timeout=self.config.request_timeout_seconds,
                    )

            except asyncio.TimeoutError:
                action_result = ActionResult(
                    status=ResultStatus.TIMEOUT,
                    confidence=0.0,
                    message="Request timed out.",
                    error=ErrorInfo(code="TIMEOUT", message="Operation timed out."),
                )
            except asyncio.CancelledError:
                action_result = ActionResult(
                    status=ResultStatus.CANCELLED,
                    confidence=0.0,
                    message="Request cancelled.",
                    error=ErrorInfo(code="CANCELLED", message="Operation cancelled."),
                )
            except Exception as exc:  # noqa: BLE001
                self.logger.exception("handle_text_unhandled error=%s", exc)
                action_result = ActionResult(
                    status=ResultStatus.FAILED,
                    confidence=0.0,
                    message="Execution failed safely.",
                    error=ErrorInfo(code="HANDLE_TEXT_FAILURE", message=str(exc)),
                )

            action_result.message = self.personality.apply_style(action_result.message, tone)
            action_result.metadata.update({"tone": tone, **tone_meta})
            if intent is not None:
                self.context.record_interaction(text=text, intent=intent, result=action_result)

            report = ExecutionReport(
                status=action_result.status,
                confidence=action_result.confidence,
                correlation_id=correlation_id,
                route=decision_route,
                metadata={
                    "reason": decision_reason,
                    **action_result.metadata,
                    "metrics": self.metrics.snapshot(),
                    "circuit_open": self.circuit_breaker.state().is_open,
                },
                error=action_result.error,
                started_at=started_at,
                finished_at=datetime.now(tz=timezone.utc),
            )
            return self._response_from_report(report)

    def _response_from_report(self, report: ExecutionReport) -> AssistantResponse:
        text = "Done." if report.status == ResultStatus.SUCCESS else "Request failed safely."
        if report.error:
            text = f"{text} ({report.error.message})"
        return AssistantResponse(
            text=text,
            executed=report.status == ResultStatus.SUCCESS,
            metadata={
                "route": report.route,
                "status": report.status.value,
                "correlation_id": report.correlation_id,
                "confidence": report.confidence,
                **report.metadata,
            },

    def handle_text(self, text: str) -> AssistantResponse:
        intent = self.nlp.parse(text)
        complexity = self.reasoning.estimate_complexity(text, intent)
        decision = self.decision_engine.decide(
            mode=self.config.mode,
            intent=intent,
            is_sensitive=self.permissions.is_sensitive_intent(intent.intent),
            complexity_score=complexity,
        )
        plan = self.reasoning.create_plan(text=text, intent=intent, route=decision.route)
        if plan.requires_confirmation and not self.permissions.confirm(plan.name):
            return AssistantResponse(text="Cancelled by safety policy.", executed=False)

        result = self.executor.execute_plan(plan)
        self.context.record_interaction(text=text, intent=intent, result=result)
        return AssistantResponse(
            text=result.get("message", "Done."),
            executed=result.get("success", False),
            metadata={"route": decision.route, "reason": decision.reason},
        )
