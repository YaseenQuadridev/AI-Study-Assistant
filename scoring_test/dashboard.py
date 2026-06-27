"""dashboard.py — Streamlit analytics dashboard."""
from __future__ import annotations

import streamlit as st

from predictor import compute_readiness, detect_weak_topics, trend_analysis
from services import get_plan, load_app_state

st.set_page_config(page_title="Adaptive Study Planner", layout="wide")

state = load_app_state()

st.title("Adaptive Study Planner")
st.caption("Knowledge First. Rendering Second. AI Third.")
st.divider()

readiness = compute_readiness(state)
weak = detect_weak_topics(state)
plan = get_plan(state)

# Overview
st.subheader("Overview")
c1, c2, c3 = st.columns(3)
c1.metric("Readiness", f"{readiness['label']}\n({readiness['value']})")
c2.metric("Topics", len(state["topics"]))
c3.metric("Day", state["current_day"])

# Focus
st.divider()
st.subheader("Focus Now")
if plan["plan"]:
    top = plan["plan"][0]["topic"]
    st.write(f"**{top['name']}** — {top['priority']} priority | Score {top['score']} | Memory {top['memory_strength']}")
    st.write(f"Reasons: {', '.join(top['reasons'])}")
else:
    st.info("No plan available yet.")

# Weak topics
st.divider()
st.subheader("Weak Topics")
if weak:
    for t in weak:
        color = "#ef4444" if t["confidence"] < 0.5 else "#f59e0b"
        st.markdown(f"- **{t['name']}** — confidence {t['confidence']}, mistakes {t['mistakes']}, last studied day {t['last_studied']}")
else:
    st.success("Great job! No weak topics detected.")

# Topic details
st.divider()
st.subheader("All Topics")
if state["topics"]:
    from services import enrich_topic
    data = [enrich_topic(t) for t in state["topics"]]
    st.dataframe(data, use_container_width=True)
else:
    st.info("Add topics to see details.")

# Trends
st.divider()
st.subheader("Trends")
trends = trend_analysis(state)
if trends.get("days"):
    st.line_chart({"Mistakes": trends["mistakes"], "Time (min)": trends["time_spent"]}, x=trends["days"])
else:
    st.info(trends.get("message", "Study more to see trends."))
