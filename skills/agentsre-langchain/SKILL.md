---
name: agentsre-langchain
description: Add SRE monitoring to LangChain agents with the agentsre-langchain package. Use when wrapping a LangChain agent or chain to record decision quality, tool-call efficiency, escalation rate and cost, or to count and block duplicate tool calls caused by retries.
---

# agentsre-langchain

Semantic SLI monitoring for LangChain agents. Wrap the function that runs the agent; read
SLIs from a collector.

Install: `pip install agentsre-langchain`

## Monitor a sync agent

```python
from agentsre_langchain import MetricsCollector, monitor_agent

collector = MetricsCollector(tie_baseline_calls=3.0)

@monitor_agent("payment-router", "payments", collector=collector)
def run_agent(query: str) -> dict:
    return executor.invoke({"input": query})

run_agent("route this payment")
print(collector.get_summary("payments"))   # dqr, tie, her, cost, avg_time_ms
```

The decorated function should return a dict. Keys `confidence`, `tool_calls`, `input_tokens`,
`output_tokens` and `cost` are read when present; other return types are still counted.
Exceptions are recorded as failures and re-raised.

## Async chains

```python
from agentsre_langchain import async_monitor_agent

@async_monitor_agent("triage", "alerts", collector=collector)
async def run(query: str) -> dict:
    return await chain.ainvoke({"input": query})
```

## Shared collector shortcut

If `collector` is omitted, a process-wide collector is used. Read it with
`get_metrics("payments")`; call `reset_default_collector()` between tests.

## Block duplicate tool calls

```python
from agentsre_langchain import DuplicateToolCallGuard

guard = DuplicateToolCallGuard(window_seconds=300, raise_on_duplicate=False)
decision = guard.check("create_payment", '{"to": "acct-9", "amount": 120}')
if not decision.allowed:
    ...  # a retry would write twice
```

## Guidance

- Pass one collector per agent in services and tests so state stays isolated.
- Set `tie_baseline_calls` to the tool calls a healthy task needs.
- Export `get_summary()` values to your metrics backend and alert on them.
- Run tests with `pytest -q`.
