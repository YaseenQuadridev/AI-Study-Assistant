"""speech_provider.py — Abstract TTS + concrete implementations."""
from __future__ import annotations

import hashlib
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class SpeechProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, voice: str = "default", speed: float = 1.0) -> bytes:
        ...

    def cache_path(self, text: str, voice: str, speed: float, cache_dir: Path) -> Path:
        h = hashlib.sha256(f"{text}:{voice}:{speed}".encode()).hexdigest()[:16]
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / f"{h}.wav"


class KokoroSpeechProvider(SpeechProvider):
    def __init__(self, cache_dir: Path | str = "./audio_cache"):
        self.cache_dir = Path(cache_dir)
        self._pipeline = None

    def _load(self):
        if self._pipeline is None:
            try:
                from kokoro import KPipeline
                self._pipeline = KPipeline(lang_code="a")
            except Exception as e:
                raise RuntimeError(f"Failed to load Kokoro: {e}")

    def synthesize(self, text: str, voice: str = "af_heart", speed: float = 1.0) -> bytes:
        path = self.cache_path(text, voice, speed, self.cache_dir)
        if path.exists():
            return path.read_bytes()
        self._load()
        generator = self._pipeline(text, voice=voice, speed=speed)
        audio = None
        for _, _, data in generator:
            audio = data
        if audio is None:
            raise RuntimeError("Kokoro produced no audio")
        import soundfile as sf
        import io
        buf = io.BytesIO()
        sf.write(buf, audio, 24000, format="WAV")
        wav = buf.getvalue()
        path.write_bytes(wav)
        return wav


class ElevenLabsSpeechProvider(SpeechProvider):
    def __init__(self, api_key: str, cache_dir: Path | str = "./audio_cache"):
        self.api_key = api_key
        self.cache_dir = Path(cache_dir)

    def synthesize(self, text: str, voice: str = "default", speed: float = 1.0) -> bytes:
        path = self.cache_path(text, voice, speed, self.cache_dir)
        if path.exists():
            return path.read_bytes()
        import requests
        r = requests.post(
            "https://api.elevenlabs.io/v1/text-to-speech/" + voice,
            headers={"xi-api-key": self.api_key, "Content-Type": "application/json"},
            json={"text": text, "model_id": "eleven_turbo_v2"},
            timeout=60,
        )
        r.raise_for_status()
        wav = r.content
        path.write_bytes(wav)
        return wav
