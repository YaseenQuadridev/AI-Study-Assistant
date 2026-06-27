"""rendering/slides_renderer.py"""
from __future__ import annotations

from typing import Any

from .base_renderer import BaseRenderer


class SlidesRenderer(BaseRenderer):
    def render(self, content: dict[str, Any], **kwargs: Any) -> str:
        title = content.get("title", "Slides")
        points = content.get("points", [])
        slides = [f"# {title}\n"]
        for i, point in enumerate(points, 1):
            slides.append(f"## Slide {i}\n\n{point}\n")
        return "\n---\n\n".join(slides)
