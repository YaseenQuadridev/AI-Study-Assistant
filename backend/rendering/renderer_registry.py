"""rendering/renderer_registry.py — Pluggable renderer system."""
from __future__ import annotations

from typing import Any

from .text_renderer import TextRenderer
from .markdown_renderer import MarkdownRenderer
from .html_renderer import HTMLRenderer
from .slides_renderer import SlidesRenderer
from .quiz_renderer import QuizRenderer
from .flashcard_renderer import FlashcardRenderer
from .audio_renderer import AudioRenderer


class RendererRegistry:
    _renderers: dict[str, Any] = {}

    @classmethod
    def register(cls, name: str, renderer: Any) -> None:
        cls._renderers[name] = renderer

    @classmethod
    def get(cls, name: str) -> Any:
        return cls._renderers.get(name)

    @classmethod
    def render(cls, name: str, content: dict[str, Any], **kwargs: Any) -> Any:
        renderer = cls._renderers.get(name)
        if not renderer:
            raise ValueError(f"Renderer '{name}' not found")
        return renderer.render(content, **kwargs)

    @classmethod
    def list_renderers(cls) -> list[str]:
        return list(cls._renderers.keys())


# Register defaults
RendererRegistry.register("text", TextRenderer())
RendererRegistry.register("markdown", MarkdownRenderer())
RendererRegistry.register("html", HTMLRenderer())
RendererRegistry.register("slides", SlidesRenderer())
RendererRegistry.register("quiz", QuizRenderer())
RendererRegistry.register("flashcards", FlashcardRenderer())
RendererRegistry.register("audio", AudioRenderer())
