"""
Decorators for monitoring LangChain agent execution.

Two decorators are provided — one synchronous, one async — so they can wrap
both standard callables and async LangChain chains without blocking the event
loop.

Usage
-----
Sync agent::

    from agentsre_langchain import monitor_agent

    collector = MetricsCollector(tie_baseline_calls=3.0)

    @monitor_agent(agent_id="payment-router", task_class="payments",
                   collector=collector)
    def run_agent(query: str) -> dict:
        return executor.invoke({"input": query})

Async agent::

    from agentsre_langchain import async_monitor_agent

    @async_monitor_agent(agent_id="alert-triage", task_class="triage",
                         collector=collector)
    async def run_async_agent(query: str) -> dict:
        return await chain.ainvoke({"input": query})

The collector instance is passed explicitly (not a module-level global) so
multiple agents, test suites, and concurrent workers can each maintain
isolated metric state.
"""

from __future__ import annotations

import asyncio
import functools
import time
import logging
from typing import Any, Callable, Optional

from .collector import ExecutionMetrics, MetricsCollector

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Synchronous decorator
# ---------------------------------------------------------------------------

def monitor_agent(
    agent_id:   str,
    task_class: str,
    collector:  MetricsCollector,
    *,
    verbose:    bool = False,
) -> Callable:
    """
    Decorator that records SRE metrics for a synchronous LangChain agent.

    Parameters
    ----------
    agent_id   : Unique identifier for this agent instance.
    task_class : Task category label (e.g. "payments", "alert_triage").
    collector  : MetricsCollector instance to record into.
    verbose    : Log SLI summary after each execution.

    The decorated function must return a dict (standard LangChain pattern).
    If it returns a non-dict the decorator still records success/failure but
    leaves token/cost metrics as zero.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000

                metrics = _extract_metrics(
                    result, agent_id=agent_id,
                    task_class=task_class,
                    success=True,
                    elapsed_ms=elapsed_ms,
                )
                collector.record(metrics)

                if verbose:
                    summary = collector.get_summary(task_class)
                    logger.info(
                        "Agent %s completed | DQR=%.1f%% TIE=%.2f HER=%.1f%%",
                        agent_id,
                        summary.get("dqr", 0.0),
                        summary.get("tie", 0.0),
                        summary.get("her", 0.0),
                    )

                return result

            except Exception:
                elapsed_ms = (time.perf_counter() - start) * 1000
                collector.record(ExecutionMetrics(
                    agent_id=agent_id,
                    task_class=task_class,
                    success=False,
                    execution_time_ms=elapsed_ms,
                ))
                logger.error("Agent %s failed after %.0f ms", agent_id, elapsed_ms)
                raise

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# Async decorator
# ---------------------------------------------------------------------------

def async_monitor_agent(
    agent_id:   str,
    task_class: str,
    collector:  MetricsCollector,
    *,
    verbose:    bool = False,
) -> Callable:
    """
    Decorator that records SRE metrics for an *async* LangChain agent.

    Drop-in replacement for ``monitor_agent`` when wrapping coroutines.
    Uses ``time.perf_counter()`` (not asyncio.sleep) so it measures wall
    clock time without blocking the event loop.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000

                metrics = _extract_metrics(
                    result, agent_id=agent_id,
                    task_class=task_class,
                    success=True,
                    elapsed_ms=elapsed_ms,
                )
                collector.record(metrics)

                if verbose:
                    summary = collector.get_summary(task_class)
                    logger.info(
                        "Async agent %s completed | DQR=%.1f%% TIE=%.2f HER=%.1f%%",
                        agent_id,
                        summary.get("dqr", 0.0),
                        summary.get("tie", 0.0),
                        summary.get("her", 0.0),
                    )

                return result

            except Exception:
                elapsed_ms = (time.perf_counter() - start) * 1000
                collector.record(ExecutionMetrics(
                    agent_id=agent_id,
                    task_class=task_class,
                    success=False,
                    execution_time_ms=elapsed_ms,
                ))
                logger.error("Async agent %s failed after %.0f ms", agent_id, elapsed_ms)
                raise

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_metrics(
    result:     Any,
    agent_id:   str,
    task_class: str,
    success:    bool,
    elapsed_ms: float,
) -> ExecutionMetrics:
    """Extract ExecutionMetrics from a LangChain result dict (best-effort)."""
    if not isinstance(result, dict):
        return ExecutionMetrics(
            agent_id=agent_id,
            task_class=task_class,
            success=success,
            execution_time_ms=elapsed_ms,
        )
    return ExecutionMetrics(
        agent_id=agent_id,
        task_class=task_class,
        tool_calls=result.get("tool_calls", 1),
        success=success,
        confidence=float(result.get("confidence", 0.9)),
        input_tokens=result.get("input_tokens", 0),
        output_tokens=result.get("output_tokens", 0),
        cost=float(result.get("cost", 0.0)),
        execution_time_ms=elapsed_ms,
    )
