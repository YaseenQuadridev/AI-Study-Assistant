"""flask_app.py — Flask API and web UI."""
from __future__ import annotations

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
CORS(app)


def envelope(ok, data=None, error=None):
    return jsonify({"ok": ok, "data": data, "error": error})


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
    state = load_app_state()
    topic = add_topic(
        state,
        subject or "General",
        name,
        float(payload.get("D", 0.5)),
        float(payload.get("P", 0.5)),
        float(payload.get("U", 0.5)),
    )
    save_app_state(state)
    return envelope(True, topic)


@app.route("/log", methods=["POST"])
def api_log():
    payload = request.get_json(force=True) or {}
    name = payload.get("topic_name") or payload.get("name")
    if not name:
        return envelope(False, error="topic_name required"), 400
    state = load_app_state()
    try:
        log_study_session(
            state, name, payload.get("studied_today", True), payload.get("made_mistake", False)
        )
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
    state = load_app_state()
    try:
        log_detailed_performance(
            state,
            name,
            float(payload["accuracy"]),
            float(payload["recall_quality"]),
            int(payload["time_taken"]),
            int(payload["expected_time"]),
        )
    except (KeyError, ValueError) as e:
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
    app.run(debug=True, port=5000)
