"""rendering/base_renderer.py — Abstract renderer."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseRenderer(ABC):
    @abstractmethod
    def render(self, content: dict[str, Any], **kwargs: Any) -> Any:
        ...
