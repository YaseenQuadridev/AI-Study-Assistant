"""cli.py — Command-line interface for Adaptive Study Planner."""
from __future__ import annotations

import argparse

from predictor import compute_readiness, detect_weak_topics, trend_analysis
from services import advance_day, get_plan, load_app_state, log_study_session, save_app_state


def cmd_plan(args):
    state = load_app_state()
    result = get_plan(state)
    print(f"Day {state['current_day']} — Study Plan ({result['total_minutes']} min)")
    print("-" * 40)
    for i, item in enumerate(result["plan"], 1):
        t = item["topic"]
        print(f"{i}. {t['name']} ({t['priority']}) — {item['estimated_minutes']} min")
        print(f"   Score: {t['score']} | Memory: {t['memory_strength']} | Reasons: {', '.join(t['reasons'])}")
    if result["overflow_count"]:
        print(f"\nOverflow: {result['overflow_count']} topics not scheduled (180-min cap)")


def cmd_dashboard(args):
    state = load_app_state()
    readiness = compute_readiness(state)
    weak = detect_weak_topics(state)
    print(f"Readiness: {readiness['label']} ({readiness['value']})")
    print(f"Topics: {len(state['topics'])}")
    if weak:
        print("Weak topics:")
        for t in weak:
            print(f"  - {t['name']} (conf {t['confidence']}, mistakes {t['mistakes']})")
    else:
        print("No weak topics detected.")


def cmd_log(args):
    state = load_app_state()
    topic = input("Topic name: ").strip()
    studied = input("Studied today? (y/n): ").strip().lower() == "y"
    mistake = input("Made mistake? (y/n): ").strip().lower() == "y"
    log_study_session(state, topic, studied, mistake)
    save_app_state(state)
    print("Logged.")


def cmd_predict(args):
    state = load_app_state()
    readiness = compute_readiness(state)
    trends = trend_analysis(state)
    print(f"Readiness: {readiness['label']} ({readiness['value']})")
    if trends.get("days"):
        print(f"Trend days: {trends['days']}")
        print(f"Mistakes per day: {trends['mistakes']}")
        print(f"Time per day: {trends['time_spent']}")
    else:
        print(trends.get("message", "No trends yet."))


def main():
    parser = argparse.ArgumentParser(description="Adaptive Study Planner CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan", help="Generate today's study plan")
    sub.add_parser("dashboard", help="Show readiness and weak topics")
    sub.add_parser("log", help="Log a study session")
    sub.add_parser("predict", help="Show predictions and trends")
    args = parser.parse_args()
    if args.cmd == "plan":
        cmd_plan(args)
    elif args.cmd == "dashboard":
        cmd_dashboard(args)
    elif args.cmd == "log":
        cmd_log(args)
    elif args.cmd == "predict":
        cmd_predict(args)


if __name__ == "__main__":
    main()
