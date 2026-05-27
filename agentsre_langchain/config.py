"""Configuration for agentsre-langchain monitoring."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MonitorConfig:
    """Configuration for agent monitoring."""
    
    track_tokens: bool = True
    track_decisions: bool = True
    track_escalations: bool = True
    track_cost: bool = True
    alert_on_breach: bool = True
    dqr_threshold: float = 85.0
    tie_threshold: float = 1.5
    her_threshold: float = 5.0
    verbose: bool = False
