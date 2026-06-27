"""predictor.py — Readiness, confidence, weak topics, trends."""
from __future__ import annotations

from typing import Any

from services import enrich_topic, memory_strength


def compute_confidence(topic: dict[str, Any], current_day: int) -> float:
    fb = topic.get("last_feedback")
    if fb:
        base = 0.6 * float(fb.get("accuracy", 0.5)) + 0.4 * float(fb.get("recall_quality", 0.5))
    else:
        base = 0.5
    mem = memory_strength(topic, current_day)
    score = float(topic.get("score", 0.0))
    conf = base * (0.5 + 0.5 * mem) * (0.7 + 0.3 * score)
    return round(max(0.0, min(1.0, conf)), 4)


def confidence_label(conf: float) -> str:
    if conf > 0.75:
        return "High"
    if conf >= 0.5:
        return "Medium"
    return "Low"


def compute_readiness(state: dict[str, Any]) -> dict[str, Any]:
    topics = state.get("topics", [])
    current_day = int(state.get("current_day", 1))
    if not topics:
        return {"value": 0.0, "label": "N/A"}
    enriched = [enrich_topic(t) for t in topics]
    confidences = [compute_confidence(t, current_day) for t in enriched]
    weights = [t["score"] for t in enriched]
    total_w = sum(weights) or 1.0
    readiness = sum(c * w for c, w in zip(confidences, weights)) / total_w
    readiness = round(readiness, 4)
    if readiness > 0.7:
        label = "Strong"
    elif readiness >= 0.5:
        label = "Medium"
    else:
        label = "Weak"
    return {"value": readiness, "label": label}


def detect_weak_topics(state: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    current_day = int(state.get("current_day", 1))
    topics = state.get("topics", [])
    if not topics:
        return []
    enriched = [enrich_topic(t) for t in topics]
    for t in enriched:
        t["confidence"] = compute_confidence(t, current_day)
        t["memory_strength"] = memory_strength(t, current_day)
    # Sort: confidence asc, mistakes desc, last_studied asc (None = oldest)
    enriched.sort(key=lambda t: (t["confidence"], -t.get("mistakes", 0), t.get("last_studied") or -1))
    weak = enriched[:limit]
    return [{"name": t["name"], "confidence": t["confidence"], "mistakes": t.get("mistakes", 0), "last_studied": t.get("last_studied")} for t in weak]


def trend_analysis(state: dict[str, Any]) -> dict[str, Any]:
    hist = state.get("performance_history", [])
    if not hist:
        return {"days": [], "mistakes": [], "time_spent": [], "message": "Study more to see trends."}
    # Records written by log_detailed_performance have: accuracy, recall_quality, time_taken, expected_time, day, topic
    # We only need 'day' and 'time_taken'; 'mistakes' is optional and defaults to 0.
    if "day" not in hist[0]:
        return {"days": [], "mistakes": [], "time_spent": [], "message": "History data incomplete"}
    days = sorted({int(h["day"]) for h in hist})
    by_day = {}
    for h in hist:
        d = int(h["day"])
        by_day.setdefault(d, {"mistakes": 0, "time_taken": 0})
        by_day[d]["mistakes"] += int(h.get("mistakes", 0))
        by_day[d]["time_taken"] += int(h.get("time_taken", 0))
    return {
        "days": days,
        "mistakes": [by_day.get(d, {}).get("mistakes", 0) for d in days],
        "time_spent": [by_day.get(d, {}).get("time_taken", 0) for d in days],
    }
