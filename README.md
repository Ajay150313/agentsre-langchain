# agentsre-langchain

**Semantic SLI monitoring for LangChain agents** — Track Decision Quality, Tool Efficiency, Escalations, and Queue Depth in production.

[![PyPI version](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/project/agentsre-langchain/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## The Problem

You're running LangChain agents in production.

Your agent returns HTTP 200. All tool calls succeed. Every health check passes.

**But it's making wrong decisions 30% of the time.**

Your existing monitoring won't catch this until it causes business impact.

---

## The Solution

Track the four semantic SLIs that matter:

| SLI | What it measures | Healthy | Alert |
|-----|------------------|---------|-------|
| **DQR** | Decision Quality Rate | >92% | <85% |
| **TIE** | Tool Invocation Efficiency | 1.0-1.2x | >1.5x |
| **HER** | Human Escalation Rate | <2% | >5% |
| **AQDD** | Queue Depth Drift | <20 | >50 |

---

## Install

```bash
# Basic installation
pip install agentsre-langchain

# With agentsre integration
pip install agentsre-langchain agentsre
```

---

## Quick Start

```python
from langchain.agents import AgentExecutor
from agentsre_langchain import monitor_agent, MonitorConfig

@monitor_agent(
    agent_id="payment-router",
    task_class="payments",
    config=MonitorConfig(verbose=True, track_cost=True)
)
def run_agent(query: str):
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor.invoke({"input": query})

# Now every execution is monitored
result = run_agent("Route this payment...")

# Get metrics
from agentsre_langchain import get_metrics
metrics = get_metrics("payments")
print(f"DQR: {metrics['dqr']}%")
print(f"TIE: {metrics['tie']}x")
print(f"HER: {metrics['her']}%")
print(f"Cost: ${metrics['total_cost']:.4f}")
```

---

## Examples

1. **Simple Agent** - `examples/1_simple_agent.py`
   - Basic monitoring with decorator

2. **Multi-Tool Routing** - `examples/2_multi_tool_agent.py`
   - Track tool selection efficiency

3. **ReAct Pattern** - `examples/3_react_agent.py`
   - Monitor reasoning + acting agents

4. **With Memory** - `examples/4_with_memory.py`
   - Track conversation context overhead

5. **Cost Optimization** - `examples/5_cost_tracking.py`
   - Monitor reliability AND cost together

---

## Integration with agentsre

If you have `agentsre` installed, metrics automatically flow through:

```python
from agentsre_langchain.integrations import integrate_with_agentsre

# Automatic integration
metrics = get_metrics("payment_routing")
agentsre_results = integrate_with_agentsre(
    agent_id="payment-router",
    task_class="payment_routing",
    metrics=metrics
)
```

---

## Configuration

```python
from agentsre_langchain import MonitorConfig

config = MonitorConfig(
    track_tokens=True,           # Track input/output tokens
    track_decisions=True,        # Track decision quality
    track_escalations=True,      # Track human escalations
    track_cost=True,             # Track API costs
    alert_on_breach=True,        # Alert when SLI breaches
    dqr_threshold=85.0,          # DQR breach threshold
    tie_threshold=1.5,           # TIE breach threshold
    her_threshold=5.0,           # HER breach threshold
    verbose=False,               # Log metrics
)

@monitor_agent("my-agent", "task_type", config=config)
def my_agent(query: str):
    ...
```

---

## How It Works

### 1. Decorator Captures Execution
```python
@monitor_agent(agent_id="my-agent", task_class="my_tasks")
def agent_function(query):
    # Your LangChain agent code
    return result
```

### 2. Metrics Extracted
- Confidence score (from agent output)
- Tool calls (how many tools invoked)
- Tokens (input/output tracking)
- Cost (API call pricing)

### 3. SLIs Calculated
- **DQR**: % of high-confidence decisions
- **TIE**: Tool calls vs baseline
- **HER**: % of failed executions
- **AQDD**: Pending items in queue

### 4. Results Available
```python
metrics = get_metrics("task_class")
# {
#   "executions": 100,
#   "dqr": 92.5,
#   "tie": 1.2,
#   "her": 2.1,
#   "total_cost": 2.45,
#   "avg_cost_per_execution": 0.0245
# }
```

---

## SLO Targets (Starting Points)

| Environment | DQR | TIE | HER | AQDD |
|-------------|-----|-----|-----|------|
| Development | >75% | <2.0x | <10% | <50 |
| Staging | >85% | <1.5x | <5% | <20 |
| Production | >92% | <1.2x | <2% | <10 |

**Rule:** Run 30-day observation window before committing to SLO targets.

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## License

MIT © [Ajay Devineni](https://linkedin.com/in/ajay-devineni)

---

**If this helps you instrument your agents, a ⭐ means a lot.**
