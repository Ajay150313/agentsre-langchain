"""
Example 4: Agent with Conversation Memory

Shows monitoring of stateful agents that maintain context.
"""

from agentsre_langchain import monitor_agent, MonitorConfig


@monitor_agent(
    agent_id="memory-agent",
    task_class="conversation",
    config=MonitorConfig(verbose=True)
)
def run_conversation_agent(user_input: str, memory_size: int) -> dict:
    """
    Simulate an agent with conversation memory.
    """
    
    confidence = 0.92
    tool_calls = 1
    
    # More memory = need to search through history
    if memory_size > 10:
        tool_calls += 1
        confidence = 0.88
    
    if memory_size > 100:
        tool_calls += 2  # Search + retrieval
        confidence = 0.80
    
    return {
        "response": f"Based on our conversation: {user_input}",
        "tool_calls": tool_calls,
        "confidence": confidence,
        "memory_tokens": memory_size * 10,
    }


# Test it
if __name__ == "__main__":
    print("=" * 60)
    print("Example 4: Agent with Conversation Memory")
    print("=" * 60)
    
    memory_sizes = [5, 15, 50, 150]
    
    for mem_size in memory_sizes:
        result = run_conversation_agent("Tell me what we discussed", mem_size)
        print(f"\nMemory Size: {mem_size} messages")
        print(f"Tool Calls: {result['tool_calls']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Memory Tokens: {result['memory_tokens']}")
    
    # Get metrics
    from agentsre_langchain import get_metrics
    
    metrics = get_metrics("conversation")
    print("\n" + "=" * 60)
    print("CONVERSATION METRICS")
    print("=" * 60)
    print(f"Conversations: {metrics['executions']}")
    print(f"DQR: {metrics['dqr']}%")
    print(f"TIE: {metrics['tie']}x")
    print(f"Memory Overhead (Tokens): {metrics['total_tokens']}")
