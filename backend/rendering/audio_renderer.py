"""rendering/audio_renderer.py — TTS-based audio generation (cached)."""
from __future__ import annotations

from typing import Any

from .base_renderer import BaseRenderer


class AudioRenderer(BaseRenderer):
    def __init__(self, speech_provider=None):
        self.speech = speech_provider

    def render(self, content: dict[str, Any], **kwargs: Any) -> bytes:
        if not self.speech:
            raise RuntimeError("No SpeechProvider configured for AudioRenderer")
        text = content.get("script", content.get("body", ""))
        voice = kwargs.get("voice", "default")
        speed = kwargs.get("speed", 1.0)
        return self.speech.synthesize(text, voice=voice, speed=speed)
