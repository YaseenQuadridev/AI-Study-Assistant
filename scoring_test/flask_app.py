"""flask_app.py — Flask API and web UI (hardened)."""
from __future__ import annotations

import os
import threading
import time
from collections import defaultdict
from typing import Any

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from predictor import compute_readiness, detect_weak_topics, trend_analysis
from services import (
    add_topic,
    advance_day,
    get_plan,
    load_app_state,
    log_detailed_performance,
    log_study_session,
    save_app_state,
)

app = Flask(__name__, template_folder="templates", static_folder="static")

# CORS: configurable origins; default to localhost only in production
_cors_origins = os.environ.get("CORS_ORIGINS", "*")
if _cors_origins != "*":
    _cors_origins = [o.strip() for o in _cors_origins.split(",")]
CORS(app, resources={r"/api/*": {"origins": _cors_origins}})

# In-memory per-IP rate limiter (simple, no external deps)
_RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", "60"))
_RATE_LIMIT_MAX = int(os.environ.get("RATE_LIMIT_MAX", "30"))
_rate_tracker: dict[str, list[float]] = defaultdict(list)
_rate_lock = threading.Lock()


def _rate_limit(ip: str) -> bool:
    now = time.time()
    with _rate_lock:
        window = [t for t in _rate_tracker[ip] if now - t < _RATE_LIMIT_WINDOW]
        _rate_tracker[ip] = window
        if len(window) >= _RATE_LIMIT_MAX:
            return False
        _rate_tracker[ip].append(now)
    return True


def envelope(ok, data=None, error=None):
    return jsonify({"ok": ok, "data": data, "error": error})


@app.before_request
def before_request():
    ip = request.remote_addr or "unknown"
    if not _rate_limit(ip):
        return envelope(False, error="Rate limit exceeded. Slow down."), 429


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/topics")
def get_topics():
    state = load_app_state()
    from services import enrich_topic
    return envelope(True, [enrich_topic(t) for t in state["topics"]])


@app.route("/add-topic", methods=["POST"])
def api_add_topic():
    payload = request.get_json(force=True) or {}
    name = (payload.get("name") or "").strip()
    subject = (payload.get("subject") or "").strip()
    if not name:
        return envelope(False, error="Topic name required"), 400

    # Validate numeric fields safely
    try:
        d_val = float(payload.get("D", 0.5))
        p_val = float(payload.get("P", 0.5))
        u_val = float(payload.get("U", 0.5))
    except (ValueError, TypeError):
        return envelope(False, error="D, P, U must be valid numbers"), 400

    state = load_app_state()
    topic = add_topic(state, subject or "General", name, d_val, p_val, u_val)
    save_app_state(state)
    return envelope(True, topic)


@app.route("/log", methods=["POST"])
def api_log():
    payload = request.get_json(force=True) or {}
    name = payload.get("topic_name") or payload.get("name")
    if not name:
        return envelope(False, error="topic_name required"), 400

    # Normalize booleans (strings like "false" are truthy in Python)
    studied = bool(payload.get("studied_today", True))
    mistake = bool(payload.get("made_mistake", False))

    state = load_app_state()
    try:
        log_study_session(state, name, studied, mistake)
    except ValueError as e:
        return envelope(False, error=str(e)), 400
    save_app_state(state)
    return envelope(True, {"message": "Logged"})


@app.route("/log-detailed", methods=["POST"])
def api_log_detailed():
    payload = request.get_json(force=True) or {}
    name = payload.get("topic_name") or payload.get("name")
    if not name:
        return envelope(False, error="topic_name required"), 400

    # Validate all required numeric fields before mutating state
    try:
        accuracy = float(payload["accuracy"])
        recall = float(payload["recall_quality"])
        time_taken = int(payload["time_taken"])
        expected = int(payload["expected_time"])
    except (KeyError, ValueError, TypeError) as e:
        return envelope(False, error=f"Invalid payload: {e}"), 400

    state = load_app_state()
    try:
        log_detailed_performance(state, name, accuracy, recall, time_taken, expected)
    except ValueError as e:
        return envelope(False, error=str(e)), 400
    save_app_state(state)
    return envelope(True, {"message": "Logged detailed"})


@app.route("/plan")
def api_plan():
    state = load_app_state()
    result = get_plan(state)
    return envelope(True, result)


@app.route("/advance", methods=["POST"])
def api_advance():
    state = load_app_state()
    advance_day(state)
    save_app_state(state)
    return envelope(True, {"current_day": state["current_day"]})


@app.route("/health")
def health():
    return envelope(True, {"status": "ok"})


@app.route("/metrics")
def metrics():
    state = load_app_state()
    return envelope(
        True,
        {
            "readiness": compute_readiness(state),
            "weak_topics": detect_weak_topics(state),
            "trends": trend_analysis(state),
        },
    )


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    app.run(debug=debug, port=int(os.environ.get("FLASK_PORT", "5000")))
