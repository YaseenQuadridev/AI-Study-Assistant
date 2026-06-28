"""citation/citation_service.py — Citation extraction, verification, evidence trace."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Citation:
    index: int
    chunk_id: str
    document_id: str
    document_name: str
    page: int
    confidence: float
    verified: bool = False
    snippet: str = ""

@dataclass
class CitationResult:
    citations: list[Citation] = field(default_factory=list)
    grounding_score: float = 0.0
    invented_count: int = 0
    verification_passed: bool = False


class CitationService:
    def __init__(self, db_client=None):
        self.db = db_client

    def extract_citations(self, text: str) -> list[int]:
        matches = re.findall(r"\[(\d+)\]", text)
        return [int(m) for m in matches]

    def verify_citations(self, response_text: str, retrieved_chunks: list[Any]) -> CitationResult:
        citation_indices = self.extract_citations(response_text)
        result = CitationResult()
        for idx in citation_indices:
            chunk_idx = idx - 1  # [1] -> index 0
            if 0 <= chunk_idx < len(retrieved_chunks):
                chunk = retrieved_chunks[chunk_idx]
                result.citations.append(Citation(
                    index=idx, chunk_id=str(chunk_idx),
                    document_id=getattr(chunk, "document_id", ""),
                    document_name=getattr(chunk, "document_name", "Unknown"),
                    page=getattr(chunk, "page", 0),
                    confidence=getattr(chunk, "confidence", 0.5),
                    verified=True,
                    snippet=getattr(chunk, "text", "")[:200]
                ))
            else:
                result.citations.append(Citation(
                    index=idx, chunk_id="", document_id="", document_name="",
                    page=0, confidence=0, verified=False, snippet="INVENTED CITATION"
                ))
                result.invented_count += 1

        if result.citations:
            verified_count = sum(1 for c in result.citations if c.verified)
            result.grounding_score = verified_count / len(result.citations)
        result.verification_passed = result.invented_count == 0 and result.grounding_score >= 0.5
        return result

    def format_citations(self, citations: list[Citation]) -> str:
        lines = []
        for c in citations:
            status = "✓" if c.verified else "✗"
            lines.append(f"[{c.index}] {c.document_name}, Page {c.page}, Confidence: {c.confidence:.2f} {status}")
        return "\n".join(lines)

    def build_evidence_trace(self, claim: str, chunk: Any) -> dict[str, Any]:
        return {
            "claim": claim,
            "chunk_id": getattr(chunk, "chunk_id", ""),
            "chunk_text": getattr(chunk, "text", "")[:500],
            "document_id": getattr(chunk, "document_id", ""),
            "document_name": getattr(chunk, "document_name", "Unknown"),
            "page": getattr(chunk, "page", 0),
            "confidence": getattr(chunk, "confidence", 0.5)
        }
