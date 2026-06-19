"""Metric collection from LangChain agent execution."""

from __future__ import annotations

import logging
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Deque, Dict, List, Optional

logger = logging.getLogger(__name__)

# Soft cap on executions kept per task class.
# Prevents OOM in long-running production processes.
_DEFAULT_MAX_HISTORY = 10_000


@dataclass
class ExecutionMetrics:
    """Metrics from a single agent execution."""

    agent_id:          str
    task_class:        str
    tool_calls:        int    = 0
    success:           bool   = True
    confidence:        float  = 0.0
    input_tokens:      int    = 0
    output_tokens:     int    = 0
    cost:              float  = 0.0
    execution_time_ms: float  = 0.0
    timestamp:         Optional[datetime] = field(default=None)

    def __post_init__(self) -> None:
        # Always store timezone-aware UTC timestamps.
        if self.timestamp is None:
            self.timestamp = datetime.now(tz=timezone.utc)


class MetricsCollector:
    """
    Collect and analyse metrics from LangChain agent executions.

    Thread-safe: all mutations are protected by a per-instance lock.

    Each task class is stored in a fixed-size deque (ring buffer) so
    memory stays bounded even in long-running production processes.

    Parameters
    ----------
    tie_baseline_calls : Expected tool calls per task; used to normalise TIE.
    dqr_confidence_threshold : Minimum confidence to count as high-quality.
    max_history : Ring-buffer size per task class.
    """

    def __init__(
        self,
        *,
        tie_baseline_calls:        float = 2.0,
        dqr_confidence_threshold:  float = 0.80,
        max_history:               int   = _DEFAULT_MAX_HISTORY,
    ) -> None:
        self._tie_baseline = tie_baseline_calls
        self._dqr_threshold = dqr_confidence_threshold
        self._max_history = max_history

        # task_class → bounded deque
        self.executions: Dict[str, Deque[ExecutionMetrics]] = {}
        self._lock = threading.Lock()

    # ── ingestion ─────────────────────────────────────────────────────────

    def record(self, metrics: ExecutionMetrics) -> None:
        """Record a single execution. Thread-safe."""
        with self._lock:
            if metrics.task_class not in self.executions:
                self.executions[metrics.task_class] = deque(maxlen=self._max_history)
            self.executions[metrics.task_class].append(metrics)
        logger.debug("Recorded %s / class=%s", metrics.agent_id, metrics.task_class)

    # ── SLI computations ──────────────────────────────────────────────────

    def get_dqr(self, task_class: str) -> float:
        """
        Decision Quality Rate — percentage of executions with confidence
        above the configured threshold.

        Returns 0.0 if no executions exist for the task class.
        """
        with self._lock:
            bucket = list(self.executions.get(task_class, []))
        if not bucket:
            return 0.0
        high_conf = sum(1 for e in bucket if e.confidence >= self._dqr_threshold)
        return (high_conf / len(bucket)) * 100.0

    def get_tie(self, task_class: str) -> float:
        """
        Tool Invocation Efficiency — ratio of average tool calls to the
        per-instance baseline (configurable; default 2.0).

        Returns 1.0 if no executions exist (nominal).
        """
        with self._lock:
            bucket = list(self.executions.get(task_class, []))
        if not bucket:
            return 1.0
        avg_calls = sum(e.tool_calls for e in bucket) / len(bucket)
        return avg_calls / self._tie_baseline if self._tie_baseline > 0 else 0.0

    def get_her(self, task_class: str) -> float:
        """
        Human Escalation Rate — percentage of failed executions.

        Returns 0.0 if no executions exist.
        """
        with self._lock:
            bucket = list(self.executions.get(task_class, []))
        if not bucket:
            return 0.0
        failed = sum(1 for e in bucket if not e.success)
        return (failed / len(bucket)) * 100.0

    # ── summaries ─────────────────────────────────────────────────────────

    def get_summary(self, task_class: str) -> Dict:
        """
        Return a dict of aggregated metrics for the given task class.

        Returns an empty dict if no executions exist.
        """
        with self._lock:
            bucket = list(self.executions.get(task_class, []))
        if not bucket:
            return {}

        total_cost   = sum(e.cost for e in bucket)
        total_tokens = sum(e.input_tokens + e.output_tokens for e in bucket)
        n = len(bucket)

        return {
            "task_class":             task_class,
            "executions":             n,
            "dqr":                    round(self.get_dqr(task_class), 2),
            "tie":                    round(self.get_tie(task_class), 3),
            "her":                    round(self.get_her(task_class), 2),
            "total_cost":             round(total_cost, 4),
            "total_tokens":           total_tokens,
            "avg_cost_per_execution": round(total_cost / n, 4),
            "avg_time_ms":            round(sum(e.execution_time_ms for e in bucket) / n, 1),
        }

    def snapshot(self) -> Dict[str, Dict]:
        """Return a summary for every registered task class."""
        with self._lock:
            classes = list(self.executions.keys())
        return {tc: self.get_summary(tc) for tc in classes}
