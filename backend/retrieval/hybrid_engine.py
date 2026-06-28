"""retrieval/hybrid_engine.py — Dense + sparse + metadata + re-ranking + RRF."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    heading: str
    document_id: str
    score: float
    source: str = ""
    confidence: float = 0.5


class HybridRetrievalEngine:
    def __init__(self, vector_store, db_client=None, reranker=None):
        self.vector_store = vector_store
        self.db = db_client
        self.reranker = reranker

    def _dense_retrieve(self, query_embedding: list[float], k: int = 10) -> list[RetrievedChunk]:
        results = self.vector_store.search(query_embedding, k)
        return [RetrievedChunk(
            chunk_id=str(i), text=r.get("text", ""), heading=r.get("heading", ""),
            document_id=r.get("document_id", ""), score=r.get("score", 0),
            source="dense", confidence=r.get("confidence", 0.5)
        ) for i, r in enumerate(results)]

    def _sparse_retrieve(self, query: str, k: int = 10) -> list[RetrievedChunk]:
        # Fallback: simple keyword matching if no BM25 index
        keywords = [w.lower() for w in query.split() if len(w) > 2]
        if not hasattr(self.vector_store, '_chunks'):
            return []
        scored = []
        for i, chunk in enumerate(self.vector_store._chunks):
            text = chunk.get("text", "").lower()
            score = sum(text.count(kw) for kw in keywords) / max(len(keywords), 1)
            if score > 0:
                scored.append((i, score, chunk))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [RetrievedChunk(
            chunk_id=str(idx), text=c.get("text", ""), heading=c.get("heading", ""),
            document_id=c.get("document_id", ""), score=sc, source="sparse", confidence=c.get("confidence", 0.5)
        ) for idx, sc, c in scored[:k]]

    def _metadata_filter(self, candidates: list[RetrievedChunk], filters: dict[str, Any]) -> list[RetrievedChunk]:
        if not filters:
            return candidates
        result = []
        for c in candidates:
            ok = True
            if "subject" in filters and c.heading != filters["subject"]:
                ok = False
            if "confidence_min" in filters and c.confidence < filters["confidence_min"]:
                ok = False
            if "document_id" in filters and c.document_id != filters["document_id"]:
                ok = False
            if ok:
                result.append(c)
        return result

    def _source_rank(self, candidates: list[RetrievedChunk]) -> list[RetrievedChunk]:
        source_boost = {"official": 1.5, "publisher": 1.2, "user": 1.0, "coaching": 0.9, "community": 0.8}
        for c in candidates:
            boost = source_boost.get(c.source, 1.0)
            c.score *= boost
        return candidates

    def _rrf_fusion(self, lists: list[list[RetrievedChunk]], k: int = 60) -> list[RetrievedChunk]:
        scores: dict[str, float] = {}
        chunks: dict[str, RetrievedChunk] = {}
        for lst in lists:
            for rank, chunk in enumerate(lst):
                if chunk.chunk_id not in chunks:
                    chunks[chunk.chunk_id] = chunk
                scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0) + 1.0 / (k + rank + 1)
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        return [chunks[i] for i in sorted_ids]

    def _re_rank(self, candidates: list[RetrievedChunk], query: str) -> list[RetrievedChunk]:
        if self.reranker is None:
            return candidates
        try:
            pairs = [(query, c.text) for c in candidates]
            scores = self.reranker.score(pairs)
            for c, s in zip(candidates, scores):
                c.score = s
            return sorted(candidates, key=lambda x: x.score, reverse=True)
        except Exception:
            return candidates

    def retrieve(self, query: str, query_embedding: list[float], filters: dict[str, Any] = None, k: int = 5) -> list[RetrievedChunk]:
        dense = self._dense_retrieve(query_embedding, k=10)
        sparse = self._sparse_retrieve(query, k=10)
        combined = self._rrf_fusion([dense, sparse])
        if filters:
            combined = self._metadata_filter(combined, filters)
        combined = self._source_rank(combined)
        combined = self._re_rank(combined, query)
        return combined[:k]
