"""knowledge/vector_store.py — FAISS-based vector store with persistence."""
from __future__ import annotations

import json
import os
import pickle
import tempfile
from pathlib import Path
from typing import Any


class VectorStore:
    def __init__(self, dim: int = 1024, index_path: Path | str | None = None):
        self.dim = dim
        self.index_path = Path(index_path) if index_path else None
        self._index = None
        self._chunks: list[dict[str, Any]] = []
        self._id_map: list[int] = []

    def _create_index(self):
        try:
            import faiss
            self._index = faiss.IndexFlatIP(self.dim)
        except Exception as e:
            raise RuntimeError(f"FAISS not available: {e}")

    def _ensure_index(self):
        if self._index is None:
            self._create_index()

    def add(self, chunks: list[dict[str, Any]], embeddings: list[list[float]]) -> None:
        import numpy as np
        self._ensure_index()
        if not chunks or not embeddings:
            return
        vectors = np.array(embeddings, dtype=np.float32)
        # Normalize for cosine similarity via inner product
        import faiss as faiss_mod
        faiss_mod.normalize_L2(vectors)
        start_id = len(self._chunks)
        self._index.add(vectors)
        self._chunks.extend(chunks)
        self._id_map.extend(range(start_id, start_id + len(chunks)))

    def search(self, query_embedding: list[float], k: int = 5) -> list[dict[str, Any]]:
        import numpy as np
        self._ensure_index()
        if not self._chunks:
            return []
        q = np.array([query_embedding], dtype=np.float32)
        import faiss as faiss_mod
        faiss_mod.normalize_L2(q)
        distances, indices = self._index.search(q, k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self._chunks):
                continue
            chunk = dict(self._chunks[idx])
            chunk["score"] = float(dist)
            results.append(chunk)
        return results

    def save(self, path: Path | str | None = None) -> None:
        path = Path(path) if path else self.index_path
        if not path:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        if self._index is not None:
            import faiss
            faiss.write_index(self._index, str(path.with_suffix(".faiss")))
        meta = {"chunks": self._chunks, "id_map": self._id_map, "dim": self.dim}
        with open(path.with_suffix(".meta"), "wb") as f:
            pickle.dump(meta, f)

    def load(self, path: Path | str | None = None) -> None:
        path = Path(path) if path else self.index_path
        if not path or not path.with_suffix(".faiss").exists():
            return
        import faiss
        self._index = faiss.read_index(str(path.with_suffix(".faiss")))
        with open(path.with_suffix(".meta"), "rb") as f:
            meta = pickle.load(f)
        self._chunks = meta["chunks"]
        self._id_map = meta["id_map"]
        self.dim = meta.get("dim", self.dim)
