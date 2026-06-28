"""tests/test_new_services.py — Tests for new Phase 4 services."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.upload_service import UploadService
from validation.document_validator import DocumentValidator
from extraction.knowledge_extractor import KnowledgeExtractor, ExtractedConcept
from knowledge.graph_service import KnowledgeGraphService, GraphNode, GraphEdge
from retrieval.hybrid_engine import HybridRetrievalEngine, RetrievedChunk
from citation.citation_service import CitationService, Citation
from collector.web_collector import WebResourceCollector, EXAM_DATABASE
from providers.llm_provider import LLMProvider


class MockLLM(LLMProvider):
    def generate(self, prompt, model=None, temperature=0.7):
        if "concepts" in prompt.lower():
            return '[{"name": "Integration", "definition": "Area under curve", "confidence": 0.9}]'
        if "formulas" in prompt.lower():
            return '[{"latex": "\\int f(x) dx", "context": "Integration", "confidence": 0.9}]'
        if "prerequisites" in prompt.lower():
            return '["Algebra", "Limits"]'
        return "Mock response"

    def chat(self, messages, model=None, temperature=0.7):
        return self.generate(messages[0]["content"] if messages else "", model, temperature)


def test_upload_service():
    svc = UploadService(storage_path="./test_uploads")
    data = b"%PDF-1.4 test pdf content"
    result = svc.upload("test.pdf", data, user_id="user1")
    assert result.status == "uploaded"
    assert result.sha256 != ""
    assert result.filename == "test.pdf"
    print("upload_service OK")


def test_upload_validation_rejects_bad_magic():
    svc = UploadService()
    data = b"NOTAPDF"
    result = svc.upload("test.pdf", data, user_id="user1")
    assert result.status == "rejected"
    print("upload_validation OK")


def test_duplicate_detection():
    svc = UploadService(storage_path="./test_uploads")
    data = b"%PDF-1.4 duplicate test"
    r1 = svc.upload("dup.pdf", data, user_id="user1")
    r2 = svc.upload("dup2.pdf", data, user_id="user1")
    assert r2.status == "duplicate"
    print("duplicate_detection OK")


def test_document_validator():
    val = DocumentValidator()
    data = b"%PDF-1.4 valid pdf"
    result = val.validate("test.pdf", data)
    assert result["valid"] is True
    assert "encoding" in result
    print("document_validator OK")


def test_knowledge_extractor():
    llm = MockLLM()
    extractor = KnowledgeExtractor(llm)
    concepts = extractor.extract_concepts("Integration is the area under a curve.")
    assert len(concepts) > 0
    assert concepts[0].name == "Integration"
    print("knowledge_extractor OK")


def test_graph_service():
    svc = KnowledgeGraphService()
    svc.add_node("calc", "Calculus", "subject", 0.9)
    svc.add_node("integ", "Integration", "concept", 0.8)
    svc.add_edge("calc", "integ", "part-of", 0.9)
    prereqs = svc.get_prerequisites("calc")
    assert "integ" in prereqs
    print("graph_service OK")


def test_hybrid_retrieval():
    from knowledge.vector_store import VectorStore
    vs = VectorStore(dim=3)
    # Add test chunks
    vs._chunks = [
        {"text": "Newton first law physics", "heading": "Physics", "document_id": "doc1", "confidence": 0.9},
        {"text": "Chemistry periodic table", "heading": "Chemistry", "document_id": "doc2", "confidence": 0.8},
    ]
    vs._index = None
    engine = HybridRetrievalEngine(vs)
    # Mock dense search by setting vector_store
    results = engine._sparse_retrieve("physics newton", k=2)
    assert len(results) > 0
    print("hybrid_retrieval OK")


def test_citation_service():
    svc = CitationService()
    class MockChunk:
        text = "Test chunk"
        document_id = "doc1"
        document_name = "Test Doc"
        page = 5
        confidence = 0.9
    chunks = [MockChunk(), MockChunk()]
    result = svc.verify_citations("Answer [1] and [2]", chunks)
    assert result.grounding_score == 1.0
    assert result.invented_count == 0
    print("citation_service OK")


def test_web_collector():
    collector = WebResourceCollector()
    info = collector.search_exam("JEE")
    assert info["found"] is True
    assert "official_urls" in info
    print("web_collector OK")


def test_exam_database():
    assert "JEE" in EXAM_DATABASE
    assert "NEET" in EXAM_DATABASE
    assert "SAT" in EXAM_DATABASE
    print("exam_database OK")


if __name__ == "__main__":
    test_upload_service()
    test_upload_validation_rejects_bad_magic()
    test_duplicate_detection()
    test_document_validator()
    test_knowledge_extractor()
    test_graph_service()
    test_hybrid_retrieval()
    test_citation_service()
    test_web_collector()
    test_exam_database()
    print("\nAll new service tests passed!")
