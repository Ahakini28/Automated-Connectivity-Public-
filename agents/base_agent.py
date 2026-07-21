"""Shared interface all agents implement."""

import logging
from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    name: str = "BaseAgent"

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.name)

    @abstractmethod
    def generate_report(self) -> dict[str, Any]:
        """Return this agent's current status as a JSON-serializable dict."""
