"""reasoning/rag_engine.py — Simplified deterministic RAG pipeline."""
from __future__ import annotations

from typing import Any


class RAGEngine:
    def __init__(self, knowledge_layer, llm_provider):
        self.knowledge = knowledge_layer
        self.llm = llm_provider

    def ask(self, question: str, k: int = 5, temperature: float = 0.3) -> dict[str, Any]:
        """Retrieve chunks, synthesize grounded answer with citations."""
        chunks = self.knowledge.search(question, k)
        if not chunks:
            return {"answer": "I don't have enough information to answer that.", "citations": [], "chunks": []}
        context = "\n\n".join([f"[{i+1}] {c['text']}" for i, c in enumerate(chunks)])
        prompt = (
            f"Use the following context to answer the question.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            f"Answer (cite sources with [n] format):"
        )
        answer = self.llm.generate(prompt, temperature=temperature)
        citations = [{"index": i + 1, "heading": c.get("heading", ""), "text": c["text"][:200]} for i, c in enumerate(chunks)]
        return {"answer": answer, "citations": citations, "chunks": chunks}

    def summarize(self, topic: str, k: int = 3) -> dict[str, Any]:
        chunks = self.knowledge.search(topic, k)
        if not chunks:
            return {"summary": "No relevant content found.", "citations": []}
        context = "\n\n".join([c["text"] for c in chunks])
        prompt = f"Summarize the following educational content in 3-5 sentences:\n\n{context}"
        summary = self.llm.generate(prompt, temperature=0.3)
        citations = [{"index": i + 1, "heading": c.get("heading", ""), "text": c["text"][:200]} for i, c in enumerate(chunks)]
        return {"summary": summary, "citations": citations}

    def explain(self, concept: str, k: int = 3) -> dict[str, Any]:
        chunks = self.knowledge.search(concept, k)
        if not chunks:
            return {"explanation": "No relevant content found.", "citations": []}
        context = "\n\n".join([c["text"] for c in chunks])
        prompt = (
            f"Explain the concept '{concept}' to a university student using only the following context.\n\n"
            f"Context:\n{context}\n\nExplanation:"
        )
        explanation = self.llm.generate(prompt, temperature=0.4)
        citations = [{"index": i + 1, "heading": c.get("heading", ""), "text": c["text"][:200]} for i, c in enumerate(chunks)]
        return {"explanation": explanation, "citations": citations}
