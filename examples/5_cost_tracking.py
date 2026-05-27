"""
Example 5: Cost Tracking with Semantic Monitoring

Monitor both reliability AND cost together.
"""

from agentsre_langchain import monitor_agent, MonitorConfig


@monitor_agent(
    agent_id="cost-aware-agent",
    task_class="cost_optimized",
    config=MonitorConfig(track_cost=True, verbose=True)
)
def run_cost_optimized_agent(model_type: str) -> dict:
    """
    Simulate model selection based on cost optimization.
    """
    
    # Different models have different costs and quality
    model_costs = {
        "gpt-4": {"cost": 0.03, "confidence": 0.95, "tokens": 500},
        "gpt-4-turbo": {"cost": 0.015, "confidence": 0.92, "tokens": 400},
        "gpt-4o": {"cost": 0.008, "confidence": 0.90, "tokens": 350},
        "claude-opus": {"cost": 0.025, "confidence": 0.94, "tokens": 450},
        "claude-haiku": {"cost": 0.0008, "confidence": 0.75, "tokens": 200},
    }
    
    model_info = model_costs.get(model_type, {"cost": 0.01, "confidence": 0.85, "tokens": 300})
    
    return {
        "model_used": model_type,
        "cost": model_info["cost"],
        "confidence": model_info["confidence"],
        "input_tokens": model_info["tokens"],
        "output_tokens": model_info["tokens"] // 2,
        "tool_calls": 1,
    }


# Test it
if __name__ == "__main__":
    print("=" * 60)
    print("Example 5: Cost-Aware Agent Optimization")
    print("=" * 60)
    
    models = ["gpt-4", "gpt-4o", "claude-opus", "claude-haiku"]
    
    for model in models:
        result = run_cost_optimized_agent(model)
        print(f"\nModel: {model}")
        print(f"Cost: ${result['cost']:.4f}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Total Tokens: {result['input_tokens'] + result['output_tokens']}")
    
    # Get metrics
    from agentsre_langchain import get_metrics
    
    metrics = get_metrics("cost_optimized")
    print("\n" + "=" * 60)
    print("COST OPTIMIZATION METRICS")
    print("=" * 60)
    print(f"Models Tested: {metrics['executions']}")
    print(f"DQR: {metrics['dqr']}%")
    print(f"TIE: {metrics['tie']}x")
    print(f"Total Cost: ${metrics['total_cost']:.4f}")
    print(f"Avg Cost per Execution: ${metrics['avg_cost_per_execution']:.4f}")
    
    # Cost optimization suggestion
    if metrics['total_cost'] > 0.10:
        print("\n💡 Suggestion: Consider using cheaper models for simple tasks")
