"""rendering/quiz_renderer.py"""
from __future__ import annotations

from typing import Any

from .base_renderer import BaseRenderer


class QuizRenderer(BaseRenderer):
    def render(self, content: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        questions = content.get("questions", [])
        rendered = []
        for i, q in enumerate(questions, 1):
            rendered.append({
                "question": f"{i}. {q['question']}",
                "options": q.get("options", []),
                "answer": q.get("answer", ""),
            })
        return {"title": content.get("title", "Quiz"), "questions": rendered}
