"""rendering/markdown_renderer.py"""
from __future__ import annotations

from typing import Any

from .base_renderer import BaseRenderer


class MarkdownRenderer(BaseRenderer):
    def render(self, content: dict[str, Any], **kwargs: Any) -> str:
        title = content.get("title", "Study Material")
        body = content.get("body", "")
        return f"# {title}\n\n{body}"
