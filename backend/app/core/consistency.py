"""
AlphaAlign — Consistency Ratio Calculation for AHP.

Implements consistency checking per the Saaty scale:
  CR ≤ 0.10: Good consistency
  0.10 < CR ≤ 0.20: Acceptable, review recommended
  CR > 0.20: Inconsistent, review recommended
"""

# Random Index (RI) values for matrices of size 1-15
# Source: Saaty (1980), extended
RANDOM_INDEX = {
    1: 0.00,
    2: 0.00,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49,
    11: 1.51,
    12: 1.54,
    13: 1.56,
    14: 1.57,
    15: 1.59,
}


def calculate_consistency_ratio(lambda_max: float, n: int) -> tuple[float, float]:
    """
    Calculate Consistency Index (CI) and Consistency Ratio (CR).

    CI = (λ_max - n) / (n - 1)
    CR = CI / RI

    Args:
        lambda_max: Principal eigenvalue from AHP.
        n: Number of criteria.

    Returns:
        Tuple of (CI, CR).
    """
    if n <= 2:
        return 0.0, 0.0

    ci = (lambda_max - n) / (n - 1)
    ri = RANDOM_INDEX.get(n, 1.59)  # Default to 1.59 for n > 15

    if ri == 0:
        return ci, 0.0

    cr = ci / ri
    return float(ci), float(cr)


def interpret_consistency(cr: float) -> str:
    """
    Interpret the consistency ratio.

    Returns:
        'good': CR ≤ 0.10
        'acceptable': 0.10 < CR ≤ 0.20
        'inconsistent': CR > 0.20
    """
    if cr <= 0.10:
        return "good"
    elif cr <= 0.20:
        return "acceptable"
    else:
        return "inconsistent"


def get_consistency_message(respondent_name: str, cr: float, status: str) -> str:
    """Generate a human-readable consistency message for a respondent."""
    if status == "good":
        return f"{respondent_name}'s responses show good consistency (CR = {cr:.3f})."
    elif status == "acceptable":
        return (
            f"{respondent_name}'s responses show acceptable but borderline consistency "
            f"(CR = {cr:.3f}). Review is recommended before finalizing."
        )
    else:
        return (
            f"{respondent_name}'s responses show high inconsistency (CR = {cr:.3f}). "
            f"Review is recommended before finalizing the result."
        )
