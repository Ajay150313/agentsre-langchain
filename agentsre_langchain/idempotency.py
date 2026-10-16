"""
Windowed guard for repeated LangChain tool calls.

A timeout-and-retry loop can invoke the same tool with the same input
twice. That is a write duplication, not a successful recovery.

Author: Ajay Devineni
License: MIT
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


def _key(name: str, input_str: str, scope: str = "") -> str:
    payload = json.dumps(
        {"n": name, "i": input_str, "s": scope},
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


@dataclass(frozen=True)
class ToolCallDecision:
    allowed: bool
    tool: str
    reason: str


class DuplicateToolCallGuard:
    """Count, and optionally block, identical tool starts inside a window."""

    def __init__(
        self,
        window_seconds: float = 300.0,
        max_repeats: int = 1,
        raise_on_duplicate: bool = False,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.window_seconds = window_seconds
        self.max_repeats = max_repeats
        self.raise_on_duplicate = raise_on_duplicate
        self._clock = clock
        self._seen: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
        self.checked = 0
        self.blocked = 0

    def check(self, tool: str, input_str: str, scope: str = "") -> ToolCallDecision:
        key = _key(tool, input_str, scope)
        now = self._clock()
        with self._lock:
            self.checked += 1
            stamps = [
                t for t in self._seen.get(key, [])
                if now - t <= self.window_seconds
            ]
            if len(stamps) >= self.max_repeats:
                self._seen[key] = stamps
                self.blocked += 1
                decision = ToolCallDecision(False, tool, "duplicate_within_window")
                if self.raise_on_duplicate:
                    raise RuntimeError(f"Duplicate tool call blocked: {tool}")
                return decision
            stamps.append(now)
            self._seen[key] = stamps
            return ToolCallDecision(True, tool, "ok")

    def on_tool_start(
        self,
        serialized: Optional[Dict[str, Any]],
        input_str: str,
        **kwargs: Any,
    ) -> ToolCallDecision:
        name = (serialized or {}).get("name", "unknown_tool")
        return self.check(name, input_str)

    @property
    def duplicate_action_rate(self) -> float:
        return self.blocked / self.checked if self.checked else 0.0
