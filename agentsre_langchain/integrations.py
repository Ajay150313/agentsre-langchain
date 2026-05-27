"""Integration with agentsre core library."""

from typing import Optional

try:
    from agentsre import AgentSLICollector, TaskRecord
    AGENTSRE_AVAILABLE = True
except ImportError:
    AGENTSRE_AVAILABLE = False


def integrate_with_agentsre(agent_id: str, task_class: str, metrics: dict) -> Optional[dict]:
    """
    Integrate metrics with agentsre core library.
    
    Args:
        agent_id: Agent identifier
        task_class: Task classification
        metrics: Metrics dictionary from collector
    
    Returns:
        agentsre results or None if agentsre not available
    """
    
    if not AGENTSRE_AVAILABLE:
        return None
    
    try:
        collector = AgentSLICollector()
        
        # Create TaskRecord
        task = TaskRecord(
            task_id=agent_id,
            task_class=task_class,
            tool_calls=metrics.get("tie", 1),
            required_escalation=metrics.get("her", 0) > 5,
            pending_approval=False,
            decision_confidence=0.9,
            completed=True,
        )
        
        # Record in agentsre
        collector.record(task)
        
        # Get agentsre results
        results = collector.collect(task_class)
        
        return {
            "dqr": metrics.get("dqr", 0),
            "tie": metrics.get("tie", 1),
            "her": metrics.get("her", 0),
            "agentsre_results": results,
        }
    
    except Exception as e:
        print(f"Error integrating with agentsre: {e}")
        return None
