"""providers/__init__.py — Provider interface registry."""
from __future__ import annotations

from .llm_provider import LLMProvider, OllamaLLMProvider, OpenAILLMProvider
from .embedding_provider import EmbeddingProvider, BAAIEmbeddingProvider, OpenAIEmbeddingProvider
from .speech_provider import SpeechProvider, KokoroSpeechProvider, ElevenLabsSpeechProvider

__all__ = [
    "LLMProvider", "OllamaLLMProvider", "OpenAILLMProvider",
    "EmbeddingProvider", "BAAIEmbeddingProvider", "OpenAIEmbeddingProvider",
    "SpeechProvider", "KokoroSpeechProvider", "ElevenLabsSpeechProvider",
]
