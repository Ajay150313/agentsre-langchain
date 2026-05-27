"""
Example 3: ReAct Agent Pattern

Demonstrates Reasoning + Acting pattern with monitoring.
"""

from agentsre_langchain import monitor_agent, MonitorConfig


@monitor_agent(
    agent_id="react-agent",
    task_class="complex_reasoning",
    config=MonitorConfig(verbose=True)
)
def run_react_agent(problem: str) -> dict:
    """
    Simulate ReAct agent (Reasoning + Acting).
    """
    
    confidence = 0.9
    tool_calls = 0
    
    # Thought 1: Analyze problem
    tool_calls += 1
    
    # Action 1: Search for relevant info
    tool_calls += 1
    
    # Thought 2: Plan approach
    # (This is reasoning, not a tool call)
    
    # Action 2: Execute solution
    tool_calls += 1
    
    # If problem is complex, need more reasoning
    if len(problem) > 50:
        tool_calls += 1  # Additional verification
        confidence = 0.82
    
    return {
        "reasoning": "Multi-step problem solving",
        "tool_calls": tool_calls,
        "confidence": confidence,
        "output": f"Solved: {problem[:30]}...",
    }


# Test it
if __name__ == "__main__":
    print("=" * 60)
    print("Example 3: ReAct Agent (Reasoning + Acting)")
    print("=" * 60)
    
    problems = [
        "What is 5 + 3?",
        "Write a Python function that sorts a list",
        "Explain the difference between REST and GraphQL APIs",
    ]
    
    for problem in problems:
        result = run_react_agent(problem)
        print(f"\nProblem: {problem}")
        print(f"Tool Calls (Actions): {result['tool_calls']}")
        print(f"Confidence: {result['confidence']:.2f}")
    
    # Get metrics
    from agentsre_langchain import get_metrics
    
    metrics = get_metrics("complex_reasoning")
    print("\n" + "=" * 60)
    print("REASONING METRICS")
    print("=" * 60)
    print(f"Executions: {metrics['executions']}")
    print(f"DQR (Quality): {metrics['dqr']}%")
    print(f"TIE (Efficiency): {metrics['tie']}x")
    print(f"HER (Escalations): {metrics['her']}%")
