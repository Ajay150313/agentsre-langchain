"""Decorators for monitoring LangChain agent execution."""

import functools
import time
import logging
from typing import Any, Callable, Optional

from .config import MonitorConfig
from .collector import MetricsCollector, ExecutionMetrics

logger = logging.getLogger(__name__)

# Global collector instance
_global_collector = MetricsCollector()


def monitor_agent(
    agent_id: str,
    task_class: str,
    config: Optional[MonitorConfig] = None
) -> Callable:
    """
    Decorator to monitor LangChain agent execution.
    
    Args:
        agent_id: Unique identifier for the agent
        task_class: Classification of the task (e.g., "payment_routing")
        config: MonitorConfig instance for customization
    
    Returns:
        Decorated function that tracks metrics
    
    Example:
        @monitor_agent(agent_id="payment-router", task_class="payments")
        def run_agent(query: str):
            executor = AgentExecutor(agent=agent, tools=tools)
            return executor.invoke({"input": query})
    """
    
    if config is None:
        config = MonitorConfig()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                # Execute the agent
                result = func(*args, **kwargs)
                execution_time_ms = (time.time() - start_time) * 1000
                
                # Extract metrics from result
                confidence = result.get("confidence", 0.9) if isinstance(result, dict) else 0.9
                tool_calls = result.get("tool_calls", 1) if isinstance(result, dict) else 1
                input_tokens = result.get("input_tokens", 0) if isinstance(result, dict) else 0
                output_tokens = result.get("output_tokens", 0) if isinstance(result, dict) else 0
                cost = result.get("cost", 0.0) if isinstance(result, dict) else 0.0
                
                # Create metrics
                metrics = ExecutionMetrics(
                    agent_id=agent_id,
                    task_class=task_class,
                    tool_calls=tool_calls,
                    success=True,
                    confidence=confidence,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=cost,
                    execution_time_ms=execution_time_ms,
                )
                
                # Record metrics
                _global_collector.record(metrics)
                
                if config.verbose:
                    logger.info(
                        f"Agent {agent_id} completed: "
                        f"DQR={_global_collector.get_dqr(task_class):.1f}%, "
                        f"TIE={_global_collector.get_tie(task_class):.2f}x, "
                        f"HER={_global_collector.get_her(task_class):.1f}%"
                    )
                
                return result
            
            except Exception as e:
                execution_time_ms = (time.time() - start_time) * 1000
                
                # Record failed execution
                metrics = ExecutionMetrics(
                    agent_id=agent_id,
                    task_class=task_class,
                    tool_calls=0,
                    success=False,
                    confidence=0.0,
                    execution_time_ms=execution_time_ms,
                )
                
                _global_collector.record(metrics)
                logger.error(f"Agent {agent_id} failed: {str(e)}")
                raise
        
        return wrapper
    
    return decorator


def get_metrics(task_class: str) -> dict:
    """Get metrics summary for a task class."""
    return _global_collector.get_summary(task_class)


def get_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return _global_collector
