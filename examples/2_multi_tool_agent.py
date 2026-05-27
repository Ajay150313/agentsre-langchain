"""
Example 2: Multi-Tool Agent with Route Selection

Shows how to monitor tool selection efficiency.
"""

from agentsre_langchain import monitor_agent, MonitorConfig


@monitor_agent(
    agent_id="router-agent",
    task_class="payment_routing",
    config=MonitorConfig(verbose=True, track_cost=True)
)
def run_router_agent(transaction: dict) -> dict:
    """
    Simulate a multi-tool routing agent.
    
    Real code would route to different tools based on transaction type.
    """
    
    amount = transaction.get("amount", 0)
    priority = transaction.get("priority", "normal")
    
    tools_called = 0
    confidence = 0.9
    
    # Tool 1: Check balance
    tools_called += 1
    
    # Tool 2: Validate transaction
    tools_called += 1
    
    if amount > 10000:
        # Tool 3: Require additional verification
        tools_called += 1
        confidence = 0.85
    
    if priority == "urgent":
        # Tool 4: Fast-track
        tools_called += 1
        confidence = 0.88
    
    return {
        "routed_to": "payment_processor",
        "confidence": confidence,
        "tool_calls": tools_called,
        "cost": 0.015,
    }


# Test it
if __name__ == "__main__":
    print("=" * 60)
    print("Example 2: Multi-Tool Routing Agent")
    print("=" * 60)
    
    transactions = [
        {"amount": 100, "priority": "normal"},
        {"amount": 15000, "priority": "normal"},
        {"amount": 500, "priority": "urgent"},
        {"amount": 50000, "priority": "urgent"},
    ]
    
    for txn in transactions:
        result = run_router_agent(txn)
        print(f"\nTransaction: ${txn['amount']} ({txn['priority']})")
        print(f"Tools Used: {result['tool_calls']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Cost: ${result['cost']:.4f}")
    
    # Get metrics
    from agentsre_langchain import get_metrics
    
    metrics = get_metrics("payment_routing")
    print("\n" + "=" * 60)
    print("ROUTING METRICS")
    print("=" * 60)
    print(f"Executions: {metrics['executions']}")
    print(f"DQR: {metrics['dqr']}%")
    print(f"TIE (Efficiency): {metrics['tie']}x baseline")
    print(f"HER: {metrics['her']}%")
    print(f"Total Cost: ${metrics['total_cost']:.4f}")
    print(f"Avg Cost per Transaction: ${metrics['avg_cost_per_execution']:.4f}")
