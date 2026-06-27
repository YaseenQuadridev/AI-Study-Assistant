"""rendering/flashcard_renderer.py"""
from __future__ import annotations

from typing import Any

from .base_renderer import BaseRenderer


class FlashcardRenderer(BaseRenderer):
    def render(self, content: dict[str, Any], **kwargs: Any) -> list[dict[str, str]]:
        cards = content.get("cards", [])
        return [{"front": c["question"], "back": c["answer"]} for c in cards]
