"""Metric collection from LangChain agent execution."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExecutionMetrics:
    """Metrics from a single agent execution."""
    
    agent_id: str
    task_class: str
    tool_calls: int = 0
    success: bool = True
    confidence: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    execution_time_ms: float = 0.0
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class MetricsCollector:
    """Collect and analyze metrics from LangChain agents."""
    
    def __init__(self):
        """Initialize collector."""
        self.executions: Dict[str, List[ExecutionMetrics]] = {}
        self.baselines: Dict[str, Dict[str, float]] = {}
    
    def record(self, metrics: ExecutionMetrics) -> None:
        """Record execution metrics."""
        if metrics.task_class not in self.executions:
            self.executions[metrics.task_class] = []
        
        self.executions[metrics.task_class].append(metrics)
        logger.info(f"Recorded {metrics.agent_id}: {metrics.task_class}")
    
    def get_dqr(self, task_class: str) -> float:
        """Get Decision Quality Rate (% of high-confidence decisions)."""
        if task_class not in self.executions:
            return 0.0
        
        executions = self.executions[task_class]
        high_confidence = sum(1 for e in executions if e.confidence > 0.8)
        
        if not executions:
            return 0.0
        
        return (high_confidence / len(executions)) * 100
    
    def get_tie(self, task_class: str) -> float:
        """Get Tool Invocation Efficiency (ratio vs baseline)."""
        if task_class not in self.executions:
            return 1.0
        
        executions = self.executions[task_class]
        avg_calls = sum(e.tool_calls for e in executions) / len(executions)
        baseline_calls = 2.0  # Normalized baseline
        
        return avg_calls / baseline_calls
    
    def get_her(self, task_class: str) -> float:
        """Get Human Escalation Rate (% of failed executions)."""
        if task_class not in self.executions:
            return 0.0
        
        executions = self.executions[task_class]
        failed = sum(1 for e in executions if not e.success)
        
        if not executions:
            return 0.0
        
        return (failed / len(executions)) * 100
    
    def get_summary(self, task_class: str) -> Dict:
        """Get summary metrics for task class."""
        if task_class not in self.executions:
            return {}
        
        executions = self.executions[task_class]
        total_cost = sum(e.cost for e in executions)
        total_tokens = sum(e.input_tokens + e.output_tokens for e in executions)
        
        return {
            "executions": len(executions),
            "dqr": round(self.get_dqr(task_class), 2),
            "tie": round(self.get_tie(task_class), 2),
            "her": round(self.get_her(task_class), 2),
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "avg_cost_per_execution": round(total_cost / len(executions) if executions else 0, 4),
        }
