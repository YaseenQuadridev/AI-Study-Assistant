"""knowledge/knowledge_layer.py — Orchestrator: parse → chunk → embed → store."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .document_parser import parse_document
from .semantic_chunker import SemanticChunker
from .vector_store import VectorStore


class KnowledgeLayer:
    def __init__(self, embedding_provider, vector_store: VectorStore | None = None, chunker: SemanticChunker | None = None):
        self.embedder = embedding_provider
        self.vector_store = vector_store or VectorStore()
        self.chunker = chunker or SemanticChunker()
        self.documents: list[dict[str, Any]] = []
        self.glossary: dict[str, str] = {}

    def ingest(self, file_path: str | Path) -> dict[str, Any]:
        doc = parse_document(file_path)
        chunks = self.chunker.chunk(doc["markdown"])
        if chunks:
            texts = [c["text"] for c in chunks]
            embeddings = self.embedder.embed(texts)
            self.vector_store.add(chunks, embeddings)
        self.documents.append(doc)
        return doc

    def search(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        q_emb = self.embedder.embed_one(query)
        return self.vector_store.search(q_emb, k)

    def save(self, path: Path | str) -> None:
        self.vector_store.save(path)

    def load(self, path: Path | str) -> None:
        self.vector_store.load(path)
