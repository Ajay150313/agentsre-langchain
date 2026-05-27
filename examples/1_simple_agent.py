"""
Example 1: Simple LangChain Agent with Monitoring

The simplest example - just add the @monitor_agent decorator.
"""

from agentsre_langchain import monitor_agent, MonitorConfig


@monitor_agent(
    agent_id="simple-agent",
    task_class="simple_tasks",
    config=MonitorConfig(verbose=True)
)
def run_simple_agent(query: str) -> dict:
    """
    Simulate a simple LangChain agent.
    
    In real code, this would be:
        executor = AgentExecutor(agent=agent, tools=tools)
        return executor.invoke({"input": query})
    """
    
    # Simulate agent execution
    if "hello" in query.lower():
        return {
            "output": "Hello! How can I help?",
            "confidence": 0.95,
            "tool_calls": 1,
        }
    else:
        return {
            "output": f"Processing: {query}",
            "confidence": 0.85,
            "tool_calls": 2,
        }


# Test it
if __name__ == "__main__":
    print("=" * 60)
    print("Example 1: Simple Agent with Monitoring")
    print("=" * 60)
    
    # Run agent multiple times
    queries = [
        "Hello, how are you?",
        "What is 2 + 2?",
        "Tell me a joke",
        "Hello again",
    ]
    
    for query in queries:
        result = run_simple_agent(query)
        print(f"\nQuery: {query}")
        print(f"Response: {result['output']}")
    
    # Get metrics
    from agentsre_langchain import get_metrics
    
    metrics = get_metrics("simple_tasks")
    print("\n" + "=" * 60)
    print("METRICS SUMMARY")
    print("=" * 60)
    print(f"Executions: {metrics['executions']}")
    print(f"DQR (Decision Quality Rate): {metrics['dqr']}%")
    print(f"TIE (Tool Invocation Efficiency): {metrics['tie']}x")
    print(f"HER (Human Escalation Rate): {metrics['her']}%")
    print(f"Total Cost: ${metrics['total_cost']:.4f}")
