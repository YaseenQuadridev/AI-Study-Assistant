"""embedding_provider.py — Abstract embeddings + concrete implementations."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        ...

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


class BAAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "BAAI/bge-large-en-v1.5", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self._model = None
        self._tokenizer = None

    def _load(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name, device=self.device)
            except Exception as e:
                raise RuntimeError(f"Failed to load BAAI model: {e}")

    def embed(self, texts: list[str]) -> list[list[float]]:
        import numpy as np
        self._load()
        vectors = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return vectors.tolist()


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
        import requests
        r = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={"input": texts, "model": self.model},
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()["data"]
        data.sort(key=lambda x: x["index"])
        return [d["embedding"] for d in data]
