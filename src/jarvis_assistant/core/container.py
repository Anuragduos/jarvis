from __future__ import annotations

import logging
from pathlib import Path

from jarvis_assistant.ai.emotion import AdaptivePersonality, EmotionalToneDetector
from jarvis_assistant.ai.nlp_engine import NLPEngine
from jarvis_assistant.ai.reasoning import ReasoningEngine
from jarvis_assistant.automation.executor import AutomationExecutor
from jarvis_assistant.cloud.model_router import ModelRouter
from jarvis_assistant.infrastructure.circuit_breaker import CircuitBreaker
from jarvis_assistant.infrastructure.errors import ErrorBoundary
from jarvis_assistant.infrastructure.hardware_profiler import HardwareProfiler
from jarvis_assistant.infrastructure.logging import StructuredLoggerFactory
from jarvis_assistant.infrastructure.metrics import MetricsCollector
from jarvis_assistant.infrastructure.rate_limiter import SlidingWindowLimiter
from jarvis_assistant.memory.context_manager import ContextManager
from jarvis_assistant.memory.store import MemoryStore
from jarvis_assistant.plugins.loader import PluginLoader
from jarvis_assistant.runtime.worker_pool import AsyncWorkerPool
from jarvis_assistant.security.permissions import PermissionManager
from jarvis_assistant.transactions.undo import CommandHistoryRegistry
from jarvis_assistant.utils.diagnostics import SelfDiagnostics
from jarvis_assistant.ai.nlp_engine import NLPEngine
from jarvis_assistant.ai.reasoning import ReasoningEngine
from jarvis_assistant.automation.executor import AutomationExecutor
from jarvis_assistant.memory.context_manager import ContextManager
from jarvis_assistant.memory.store import MemoryStore
from jarvis_assistant.security.permissions import PermissionManager

from .assistant import JarvisAssistant
from .config import AppConfig
from .decision_engine import ModeDecisionEngine


class ServiceContainer:
    """Dependency injection container for all services."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        self.logger_factory = StructuredLoggerFactory(self.config.log_file, level=log_level)
        self.logger = self.logger_factory.build("jarvis")

        self.metrics = MetricsCollector()
        self.error_boundary = ErrorBoundary(self.logger)

        self.hardware_profiler = HardwareProfiler()
        self.hardware_profile = self.hardware_profiler.profile()
        tuned_workers = min(self.config.max_workers, self.hardware_profiler.recommended_workers(self.hardware_profile))
        self.logger.info(
            "hardware_profile cpu=%s ram_gb=%.2f disk_free_gb=%.2f gpu=%s tuned_workers=%s model_tier=%s",
            self.hardware_profile.cpu_cores,
            self.hardware_profile.ram_gb,
            self.hardware_profile.disk_free_gb,
            self.hardware_profile.has_gpu,
            tuned_workers,
            self.hardware_profiler.recommended_model_tier(self.hardware_profile),
        )
        if self.hardware_profile.ram_gb < 4:
            self.logger.warning("system_underpowered low_memory_detected")

        self.worker_pool = AsyncWorkerPool(max_workers=tuned_workers)
        self.history = CommandHistoryRegistry()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.config.cloud_failure_threshold,
            cooldown_seconds=self.config.cloud_cooldown_seconds,
        )

        self.request_limiter = SlidingWindowLimiter(self.config.request_rate_limit_per_minute, 60.0)
        self.automation_limiter = SlidingWindowLimiter(self.config.automation_rate_limit_per_minute, 60.0)
        self.plugin_limiter = SlidingWindowLimiter(self.config.plugin_rate_limit_per_minute, 60.0)

        self.memory_store = MemoryStore(config)
        self.context_manager = ContextManager(self.memory_store)
        self.permissions = PermissionManager(config, self.logger)
        self.nlp = NLPEngine(self.logger)

        self.router = ModelRouter(config=config, circuit_breaker=self.circuit_breaker, logger=self.logger)
        self.reasoning = ReasoningEngine(router=self.router, logger=self.logger)

        self.plugin_loader = PluginLoader(Path("plugins"), self.error_boundary, self.logger)
        loaded_plugins = self.plugin_loader.load()
        self.plugin_registry = {plugin.metadata.name: plugin for plugin in loaded_plugins}

        self.executor = AutomationExecutor(
            permission_manager=self.permissions,
            history=self.history,
            error_boundary=self.error_boundary,
            logger=self.logger,
            plugin_registry=self.plugin_registry,
            plugin_timeout_seconds=self.config.plugin_timeout_seconds,
            automation_limiter=self.automation_limiter,
            plugin_limiter=self.plugin_limiter,
        )

        self.decision = ModeDecisionEngine(self.logger)
        self.tone_detector = EmotionalToneDetector()
        self.personality = AdaptivePersonality(level=0.5)

        self.diagnostics = SelfDiagnostics(
            config=config,
            plugin_registry=self.plugin_registry,
            hardware_profile=self.hardware_profile,
            logger=self.logger,
        )

    def build_assistant(self) -> JarvisAssistant:
        """Builds assistant orchestrator service."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.memory_store = MemoryStore(config.memory)
        self.context_manager = ContextManager(self.memory_store)
        self.permissions = PermissionManager(config.security)
        self.nlp = NLPEngine()
        self.reasoning = ReasoningEngine(config=config)
        self.executor = AutomationExecutor(permission_manager=self.permissions)
        self.decision = ModeDecisionEngine()

    def build_assistant(self) -> JarvisAssistant:
        return JarvisAssistant(
            config=self.config,
            nlp=self.nlp,
            reasoning=self.reasoning,
            executor=self.executor,
            context=self.context_manager,
            permissions=self.permissions,
            decision_engine=self.decision,
            error_boundary=self.error_boundary,
            worker_pool=self.worker_pool,
            circuit_breaker=self.circuit_breaker,
            request_limiter=self.request_limiter,
            metrics=self.metrics,
            tone_detector=self.tone_detector,
            personality=self.personality,
            logger=self.logger,
        )

    def shutdown(self) -> None:
        """Graceful shutdown for runtime resources."""

        self.worker_pool.shutdown()
        )
