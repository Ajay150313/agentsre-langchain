from agentsre_langchain.idempotency import DuplicateToolCallGuard


class Clock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


def test_blocks_identical_tool_start() -> None:
    clock = Clock()
    guard = DuplicateToolCallGuard(window_seconds=60, clock=clock)
    first = guard.on_tool_start({"name": "post_payment"}, '{"amt": 10}')
    second = guard.on_tool_start({"name": "post_payment"}, '{"amt": 10}')
    assert first.allowed
    assert not second.allowed
    assert guard.duplicate_action_rate == 0.5


def test_allows_after_window() -> None:
    clock = Clock()
    guard = DuplicateToolCallGuard(window_seconds=60, clock=clock)
    guard.on_tool_start({"name": "post_payment"}, '{"amt": 10}')
    clock.t = 61
    assert guard.on_tool_start({"name": "post_payment"}, '{"amt": 10}').allowed


def test_raise_on_duplicate() -> None:
    guard = DuplicateToolCallGuard(raise_on_duplicate=True, clock=Clock())
    guard.check("post_payment", "x")
    try:
        guard.check("post_payment", "x")
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "Duplicate tool call blocked" in str(exc)
