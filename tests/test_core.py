"""tests/test_core.py — Core logic tests."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scoring_test"))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from scorer import compute_score, classify_priority
from services import load_app_state, save_app_state, add_topic, get_plan, log_study_session, advance_day, enrich_topic
from predictor import compute_readiness, detect_weak_topics, trend_analysis


def test_scorer():
    assert compute_score(0.5, 0.9, 0.8, 0.5) == round(0.35*0.5 + 0.20*0.9 + 0.35*0.8 + 0.10*0.5, 4)
    assert classify_priority(0.75) == "High"
    assert classify_priority(0.55) == "Medium"
    assert classify_priority(0.30) == "Low"
    # P cap and U floor
    assert compute_score(0.0, 1.0, 0.0, 0.0) == round(0.20*0.9 + 0.10*0.2, 4)
    print("scorer OK")


def test_services():
    state = {
        "topics": [],
        "current_day": 1,
        "performance_history": [],
        "revision_tasks": [],
    }
    add_topic(state, "Math", "Calculus", 0.8, 0.9, 0.5)
    assert len(state["topics"]) == 1
    add_topic(state, "Math", "calculus", 0.7, 0.8, 0.6)  # duplicate update
    assert len(state["topics"]) == 1
    assert state["topics"][0]["D"] == 0.7

    plan = get_plan(state)
    assert len(plan["plan"]) == 1
    assert plan["total_minutes"] > 0

    log_study_session(state, "Calculus", True, True)
    assert state["topics"][0]["mistakes"] == 1
    assert state["topics"][0]["last_studied"] == 1

    advance_day(state)
    assert state["current_day"] == 2
    print("services OK")


def test_predictor():
    state = {
        "topics": [
            {"name": "Calculus", "subject": "Math", "D": 0.8, "P": 0.9, "U": 0.5, "S": 0.0, "mistakes": 0, "last_studied": None, "last_feedback": None, "performance_history": []},
        ],
        "current_day": 1,
        "performance_history": [],
        "revision_tasks": [],
    }
    r = compute_readiness(state)
    assert r["label"] in ("Strong", "Medium", "Weak")
    weak = detect_weak_topics(state)
    assert len(weak) == 1
    trends = trend_analysis(state)
    assert "message" in trends
    print("predictor OK")


def test_provider_interfaces():
    from providers import LLMProvider, EmbeddingProvider, SpeechProvider
    # Ensure abstract methods exist
    assert hasattr(LLMProvider, "generate")
    assert hasattr(EmbeddingProvider, "embed")
    assert hasattr(SpeechProvider, "synthesize")
    print("provider interfaces OK")


def test_renderer_registry():
    from rendering import RendererRegistry
    names = RendererRegistry.list_renderers()
    assert "text" in names
    assert "markdown" in names
    assert "html" in names
    assert "slides" in names
    assert "quiz" in names
    assert "flashcards" in names
    assert "audio" in names
    result = RendererRegistry.render("text", {"title": "Test", "body": "Hello"})
    assert "Test" in result
    print("renderers OK")


if __name__ == "__main__":
    test_scorer()
    test_services()
    test_predictor()
    test_provider_interfaces()
    test_renderer_registry()
    print("\nAll tests passed.")
