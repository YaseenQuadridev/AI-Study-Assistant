"""scorer.py — Deterministic topic scoring engine."""
from __future__ import annotations

# Weights
W_S = 0.35  # Syllabus weight
W_P = 0.20  # Past paper frequency
W_D = 0.35  # Difficulty
W_U = 0.10  # User performance

# Guards
P_CAP = 0.9
U_FLOOR = 0.2


def compute_score(S: float, P: float, D: float, U: float) -> float:
    """Weighted exam-relevance score in [0, 1]."""
    P = min(P, P_CAP)
    U = max(U, U_FLOOR)
    return round(W_S * S + W_P * P + W_D * D + W_U * U, 4)


def classify_priority(score: float) -> str:
    if score >= 0.70:
        return "High"
    if score >= 0.40:
        return "Medium"
    return "Low"
