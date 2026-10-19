"""
agentsre-langchain: LangChain integration for agentsre semantic monitoring.

Monitor your LangChain agents with semantic SLIs (DQR, TIE, HER, AQDD).

Author: Ajay Devineni
License: MIT
"""

__version__ = "0.1.1"
__author__ = "Ajay Devineni"

from .collector import ExecutionMetrics, MetricsCollector
from .decorators import (
    async_monitor_agent,
    get_default_collector,
    get_metrics,
    monitor_agent,
    reset_default_collector,
)
from .config import MonitorConfig
from .idempotency import DuplicateToolCallGuard, ToolCallDecision

__all__ = [
    "monitor_agent",
    "async_monitor_agent",
    "get_metrics",
    "get_default_collector",
    "reset_default_collector",
    "ExecutionMetrics",
    "MetricsCollector",
    "MonitorConfig",
    "DuplicateToolCallGuard",
    "ToolCallDecision",
]
