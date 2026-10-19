import asyncio

import pytest

from agentsre_langchain import (
    MetricsCollector,
    MonitorConfig,
    async_monitor_agent,
    get_metrics,
    monitor_agent,
    reset_default_collector,
)


@pytest.fixture(autouse=True)
def _isolate_default_collector():
    reset_default_collector()
    yield
    reset_default_collector()


def test_explicit_collector_records_success():
    c = MetricsCollector()

    @monitor_agent("a1", "payments", collector=c)
    def run(q):
        return {"confidence": 0.95, "tool_calls": 2}

    run("x")
    s = c.get_summary("payments")
    assert s["executions"] == 1
    assert s["her"] == 0.0


def test_failure_is_recorded_and_reraised():
    c = MetricsCollector()

    @monitor_agent("a1", "payments", collector=c)
    def run(q):
        raise RuntimeError("tool down")

    with pytest.raises(RuntimeError):
        run("x")
    assert c.get_summary("payments")["her"] == 100.0


def test_default_collector_and_get_metrics():
    @monitor_agent("a1", "triage", config=MonitorConfig(verbose=True))
    def run(q):
        return {"confidence": 0.9, "tool_calls": 1}

    run("x")
    run("y")
    assert get_metrics("triage")["executions"] == 2


def test_non_dict_result_still_counts():
    c = MetricsCollector()

    @monitor_agent("a1", "t", collector=c)
    def run(q):
        return "plain string"

    assert run("x") == "plain string"
    assert c.get_summary("t")["executions"] == 1


def test_async_decorator_records():
    c = MetricsCollector()

    @async_monitor_agent("a2", "async_t", collector=c)
    async def run(q):
        return {"confidence": 0.9, "tool_calls": 1}

    asyncio.run(run("x"))
    assert c.get_summary("async_t")["executions"] == 1


def test_collectors_are_isolated():
    c1, c2 = MetricsCollector(), MetricsCollector()

    @monitor_agent("a", "t", collector=c1)
    def run(q):
        return {}

    run("x")
    assert c1.get_summary("t")["executions"] == 1
    assert c2.get_summary("t") == {}
