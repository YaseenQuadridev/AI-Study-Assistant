"""llm_provider.py — Abstract LLM + concrete implementations."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import requests


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, model: str | None = None, temperature: float = 0.7) -> str:
        ...

    @abstractmethod
    def chat(self, messages: list[dict[str, str]], model: str | None = None, temperature: float = 0.7) -> str:
        ...


class OllamaLLMProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "llama3.1"):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    def generate(self, prompt: str, model: str | None = None, temperature: float = 0.7) -> str:
        r = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": model or self.default_model, "prompt": prompt, "stream": False, "options": {"temperature": temperature}},
            timeout=120,
        )
        r.raise_for_status()
        return r.json().get("response", "").strip()

    def chat(self, messages: list[dict[str, str]], model: str | None = None, temperature: float = 0.7) -> str:
        r = requests.post(
            f"{self.base_url}/api/chat",
            json={"model": model or self.default_model, "messages": messages, "stream": False, "options": {"temperature": temperature}},
            timeout=120,
        )
        r.raise_for_status()
        return r.json().get("message", {}).get("content", "").strip()


class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", default_model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def generate(self, prompt: str, model: str | None = None, temperature: float = 0.7) -> str:
        return self.chat([{"role": "user", "content": prompt}], model, temperature)

    def chat(self, messages: list[dict[str, str]], model: str | None = None, temperature: float = 0.7) -> str:
        r = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            json={"model": model or self.default_model, "messages": messages, "temperature": temperature},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
