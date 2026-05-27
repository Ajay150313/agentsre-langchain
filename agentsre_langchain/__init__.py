"""
agentsre-langchain: LangChain integration for agentsre semantic monitoring.

Monitor your LangChain agents with semantic SLIs (DQR, TIE, HER, AQDD).

Author: Ajay Devineni
License: MIT
"""

__version__ = "0.1.0"
__author__ = "Ajay Devineni"

from .decorators import monitor_agent
from .config import MonitorConfig

__all__ = [
    "monitor_agent",
    "MonitorConfig",
]
