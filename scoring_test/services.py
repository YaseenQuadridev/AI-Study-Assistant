"""services.py — State management, planning, enrichment, logging (with locking)."""
from __future__ import annotations

import json
import os
import tempfile
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from scorer import compute_score, classify_priority

DEFAULT_STATE_PATH = Path(__file__).with_name("state.json")
TIME_CAP_MINUTES = 180
_state_lock = threading.RLock()


@contextmanager
def state_transaction(path=None):
    """Acquire lock, load state, yield, save state. Skips save on exception."""
    path = path or DEFAULT_STATE_PATH
    with _state_lock:
        state = load_app_state(path)
        yield state
        save_app_state(state, path)


def load_app_state(path: Path | None = None) -> dict[str, Any]:
    path = path or DEFAULT_STATE_PATH
    with _state_lock:
        if not path.exists():
            return default_state()
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return default_state()
    # backward-compat defaults
    data.setdefault("topics", [])
    data.setdefault("current_day", 1)
    data.setdefault("performance_history", [])
    data.setdefault("revision_tasks", [])
    return data


def save_app_state(state, path=None):
    """Atomic JSON write with process-level locking."""
    path = path or DEFAULT_STATE_PATH
    with _state_lock:
        tmp = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(path.parent))
        json.dump(state, tmp, indent=2, ensure_ascii=False)
        tmp.close()
        os.replace(tmp.name, str(path))


def default_state() -> dict[str, Any]:
    return {
        "topics": [],
        "current_day": 1,
        "performance_history": [],
        "revision_tasks": [],
    }


def enrich_topic(topic: dict[str, Any]) -> dict[str, Any]:
    """Compute derived fields without mutating raw state."""
    t = dict(topic)
    D = float(t.get("D", 0.5))
    P = float(t.get("P", 0.5))
    U = float(t.get("U", 0.5))
    S = float(t.get("S", 0.0))
    t["score"] = compute_score(S, P, D, U)
    t["priority"] = classify_priority(t["score"])
    return t


def normalize_key(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def add_topic(state: dict[str, Any], subject: str, name: str, D: float, P: float, U: float) -> dict[str, Any]:
    key = normalize_key(name)
    for t in state["topics"]:
        if normalize_key(t["name"]) == key:
            t["D"] = max(0.0, min(1.0, float(D)))
            t["P"] = max(0.0, min(0.9, float(P)))
            t["U"] = max(0.0, min(1.0, float(U)))
            t["subject"] = subject
            return t
    topic = {
        "name": name.strip(),
        "subject": subject.strip(),
        "D": max(0.0, min(1.0, float(D))),
        "P": max(0.0, min(0.9, float(P))),
        "U": max(0.0, min(1.0, float(U))),
        "S": 0.0,
        "mistakes": 0,
        "last_studied": None,
        "last_feedback": None,
        "performance_history": [],
    }
    state["topics"].append(topic)
    return topic


def memory_strength(topic: dict[str, Any], current_day: int) -> float:
    last = topic.get("last_studied")
    if last is None:
        return 0.1
    gap = max(0, current_day - int(last))
    raw = 0.85 ** gap
    return max(0.1, round(raw, 4))


def get_reasons(topic: dict[str, Any], current_day: int) -> list[str]:
    reasons = []
    if topic.get("mistakes", 0) > 0:
        reasons.append("recent mistakes")
    mem = memory_strength(topic, current_day)
    if mem < 0.5:
        reasons.append("low retention")
    if topic.get("score", 0) > 0.7:
        reasons.append("high score")
    if not reasons:
        reasons.append("needs review")
    return reasons[:2]


def get_plan(state: dict[str, Any]) -> dict[str, Any]:
    current_day = int(state.get("current_day", 1))
    enriched = [enrich_topic(t) for t in state["topics"]]
    for t in enriched:
        t["memory_strength"] = memory_strength(t, current_day)
        t["reasons"] = get_reasons(t, current_day)

    # Sort: score desc, memory asc, mistakes desc
    enriched.sort(key=lambda t: (-t["score"], t["memory_strength"], -t.get("mistakes", 0)))

    plan = []
    total = 0
    for t in enriched:
        est = max(15, int(30 + t["D"] * 60))  # 30-90 min based on difficulty
        if total + est > TIME_CAP_MINUTES and plan:
            break
        plan.append({"topic": t, "estimated_minutes": est})
        total += est
    return {"plan": plan, "total_minutes": total, "overflow_count": max(0, len(enriched) - len(plan))}


def log_study_session(state: dict[str, Any], topic_name: str, studied_today: bool, made_mistake: bool) -> dict[str, Any]:
    key = normalize_key(topic_name)
    for t in state["topics"]:
        if normalize_key(t["name"]) == key:
            current_day = int(state["current_day"])
            if studied_today:
                t["last_studied"] = current_day
                t["S"] = min(1.0, round(t.get("S", 0.0) + 0.03, 4))
            if made_mistake:
                t["mistakes"] = t.get("mistakes", 0) + 1
            return t
    raise ValueError(f"Topic not found: {topic_name}")


def log_detailed_performance(state: dict[str, Any], topic_name: str, accuracy: float, recall_quality: float, time_taken: int, expected_time: int) -> dict[str, Any]:
    if not (0.0 <= accuracy <= 1.0):
        raise ValueError("accuracy must be between 0 and 1")
    if not (0.0 <= recall_quality <= 1.0):
        raise ValueError("recall_quality must be between 0 and 1")
    if time_taken <= 0:
        raise ValueError("time_taken must be positive")
    key = normalize_key(topic_name)
    for t in state["topics"]:
        if normalize_key(t["name"]) == key:
            fb = {
                "accuracy": accuracy,
                "recall_quality": recall_quality,
                "time_taken": time_taken,
                "expected_time": expected_time,
                "day": state["current_day"],
            }
            t["last_feedback"] = fb
            t["performance_history"] = t.get("performance_history", [])
            t["performance_history"].append(fb)
            state["performance_history"].append({"topic": t["name"], **fb})
            return t
    raise ValueError(f"Topic not found: {topic_name}")


def advance_day(state: dict[str, Any]) -> dict[str, Any]:
    state["current_day"] = int(state["current_day"]) + 1
    return state
