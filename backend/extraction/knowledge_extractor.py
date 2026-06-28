"""extraction/knowledge_extractor.py — LLM-based concept, formula, question, prerequisite extraction."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtractedConcept:
    name: str
    definition: str
    confidence: float = 0.5

@dataclass
class ExtractedFormula:
    latex: str
    context: str
    confidence: float = 0.5

@dataclass
class ExtractedQuestion:
    question_type: str
    question: str
    answer: str
    options: list[str] = field(default_factory=list)
    confidence: float = 0.5

@dataclass
class KnowledgeExtraction:
    concepts: list[ExtractedConcept] = field(default_factory=list)
    formulas: list[ExtractedFormula] = field(default_factory=list)
    questions: list[ExtractedQuestion] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    difficulty: float = 0.5
    chapters: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class KnowledgeExtractor:
    def __init__(self, llm_provider):
        self.llm = llm_provider

    def _call_llm(self, prompt: str, temperature: float = 0.3) -> str:
        return self.llm.generate(prompt, temperature=temperature)

    def extract_concepts(self, text: str) -> list[ExtractedConcept]:
        prompt = (
            "Extract key concepts and their definitions from the following educational text. "
            "Return a JSON array of objects with keys: name, definition, confidence (0-1). "
            "Only include concepts with confidence >= 0.5.\n\n"
            f"Text:\n{text[:4000]}\n\nJSON:"
        )
        try:
            raw = self._call_llm(prompt)
            data = json.loads(raw)
            return [ExtractedConcept(c["name"], c["definition"], c.get("confidence", 0.5)) for c in data if c.get("confidence", 0.5) >= 0.5]
        except Exception:
            return []

    def extract_formulas(self, text: str) -> list[ExtractedFormula]:
        # Regex for inline LaTeX
        latex_pattern = r"\$\$(.*?)\$\$|\$(.*?)\$|\\begin\{equation\}(.*?)\end\{equation\}"
        matches = re.findall(latex_pattern, text, re.DOTALL)
        formulas = []
        for m in matches:
            latex = m[0] or m[1] or m[2]
            if latex.strip():
                formulas.append(ExtractedFormula(latex.strip(), "", confidence=0.9))
        # LLM fallback for non-LaTeX formulas
        if len(formulas) < 3:
            prompt = (
                "Detect all mathematical formulas in the following text. "
                "Return JSON array with keys: latex, context, confidence.\n\n"
                f"Text:\n{text[:4000]}\n\nJSON:"
            )
            try:
                raw = self._call_llm(prompt)
                data = json.loads(raw)
                for f in data:
                    formulas.append(ExtractedFormula(f["latex"], f.get("context", ""), f.get("confidence", 0.5)))
            except Exception:
                pass
        return formulas

    def extract_questions(self, text: str) -> list[ExtractedQuestion]:
        prompt = (
            "Extract all questions from the following text (MCQ, fill-in-blank, short answer). "
            "Return JSON array with keys: type, question, answer, options (for MCQ), confidence.\n\n"
            f"Text:\n{text[:4000]}\n\nJSON:"
        )
        try:
            raw = self._call_llm(prompt)
            data = json.loads(raw)
            return [ExtractedQuestion(q["type"], q["question"], q["answer"], q.get("options", []), q.get("confidence", 0.5)) for q in data]
        except Exception:
            return []

    def extract_prerequisites(self, text: str, topic: str) -> list[str]:
        prompt = (
            f"What topics must a student already understand before learning \"{topic}\"? "
            "Return a JSON array of prerequisite topic names only.\n\n"
            f"Text:\n{text[:4000]}\n\nJSON:"
        )
        try:
            raw = self._call_llm(prompt)
            return json.loads(raw)
        except Exception:
            return []

    def estimate_difficulty(self, text: str) -> float:
        formula_density = len(re.findall(r"\$.*?\$|\begin\{equation\}", text)) / max(len(text) / 1000, 1)
        question_count = len(re.findall(r"\?|Question\s*\d+", text, re.IGNORECASE))
        word_complexity = len([w for w in text.split() if len(w) > 8]) / max(len(text.split()), 1)
        score = min(1.0, (formula_density * 0.4 + question_count * 0.05 + word_complexity * 0.3))
        return round(score, 2)

    def extract_chapters(self, text: str) -> list[str]:
        headings = re.findall(r"^#{1,2}\s+(.+)$", text, re.MULTILINE)
        return headings[:20]

    def extract_topics(self, text: str) -> list[str]:
        headings = re.findall(r"^#{3,6}\s+(.+)$", text, re.MULTILINE)
        return headings[:50]

    def extract(self, text: str, topic_hint: str = "") -> KnowledgeExtraction:
        ke = KnowledgeExtraction()
        ke.concepts = self.extract_concepts(text)
        ke.formulas = self.extract_formulas(text)
        ke.questions = self.extract_questions(text)
        ke.prerequisites = self.extract_prerequisites(text, topic_hint or "this content")
        ke.difficulty = self.estimate_difficulty(text)
        ke.chapters = self.extract_chapters(text)
        ke.topics = self.extract_topics(text)
        return ke
