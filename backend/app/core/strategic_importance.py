"""
AlphaAlign — Strategic Importance Engine.

Implements the boost/floor logic from the build paper (Section 8.2):
  Final Strategic Score = max(Base AHP Score + Strategic Boost, Strategic Importance Floor)
  Capped at 100.
"""

from typing import Dict, Optional

# Strategic Importance lookup table from the build paper
STRATEGIC_BOOST_TABLE = {
    0:  {"boost": 0,  "floor": None},
    1:  {"boost": 2,  "floor": None},
    2:  {"boost": 4,  "floor": None},
    3:  {"boost": 6,  "floor": None},
    4:  {"boost": 8,  "floor": 50},
    5:  {"boost": 10, "floor": 60},
    6:  {"boost": 12, "floor": 70},
    7:  {"boost": 15, "floor": 80},
    8:  {"boost": 20, "floor": 85},
    9:  {"boost": 25, "floor": 90},
    10: {"boost": 30, "floor": 95},
}

# Fields required when Strategic Importance >= 7
REQUIRED_JUSTIFICATION_FIELDS = [
    "justification",
    "executive_sponsor",
    "time_horizon",
    "risk_of_not_acting",
    "business_consequence",
    "review_date",
]


def calculate_final_score(
    base_score: float,
    strategic_importance: int,
) -> Dict:
    """
    Calculate the final strategic score using the boost/floor logic.

    Args:
        base_score: The pure AHP-calculated score (0-100).
        strategic_importance: The strategic importance value (0-10).

    Returns:
        Dict with:
            base_score: original score
            strategic_importance: the SI value
            boost: the boost amount applied
            floor: the floor applied (or None)
            final_score: the adjusted score
            was_boosted: whether the score was modified
            boost_explanation: human-readable explanation
    """
    si = max(0, min(10, strategic_importance))
    entry = STRATEGIC_BOOST_TABLE.get(si, {"boost": 0, "floor": None})

    boost = entry["boost"]
    floor = entry["floor"]

    boosted_score = base_score + boost
    if floor is not None:
        final_score = max(boosted_score, floor)
    else:
        final_score = boosted_score

    # Cap at 100
    final_score = min(100.0, final_score)

    was_boosted = final_score != base_score

    explanation = _build_explanation(base_score, si, boost, floor, final_score, was_boosted)

    return {
        "base_score": round(base_score, 1),
        "strategic_importance": si,
        "boost": boost,
        "floor": floor,
        "final_score": round(final_score, 1),
        "was_boosted": was_boosted,
        "boost_explanation": explanation,
    }


def validate_justification(
    strategic_importance: int,
    justification_data: Dict,
) -> list[str]:
    """
    Validate that required justification fields are present when SI >= 7.

    Returns:
        List of missing field names (empty if valid).
    """
    if strategic_importance < 7:
        return []

    missing = []
    for field in REQUIRED_JUSTIFICATION_FIELDS:
        value = justification_data.get(field, "")
        if not value or (isinstance(value, str) and not value.strip()):
            missing.append(field)

    return missing


def get_strategic_importance_label(value: int) -> str:
    """Get human-readable label for a strategic importance value."""
    labels = {
        0: "No strategic override",
        1: "Low strategic importance",
        2: "Low strategic importance",
        3: "Low strategic importance",
        4: "Moderate strategic importance",
        5: "Moderate strategic importance",
        6: "Moderate strategic importance",
        7: "High strategic importance",
        8: "High strategic importance",
        9: "Executive strategic priority",
        10: "Critical strategic imperative",
    }
    return labels.get(value, "Unknown")


def _build_explanation(
    base_score: float,
    si: int,
    boost: int,
    floor: Optional[int],
    final_score: float,
    was_boosted: bool,
) -> str:
    """Build a transparent explanation of how the score was adjusted."""
    if not was_boosted:
        return "No strategic adjustment applied."

    label = get_strategic_importance_label(si)
    parts = [
        f"Base AHP Score: {base_score:.1f}.",
        f"Strategic Importance: {si} ({label}).",
    ]

    if floor is not None and final_score == floor:
        parts.append(
            f"The strategic importance floor of {floor} was applied, "
            f"lifting the score from {base_score:.1f} to {final_score:.1f}."
        )
    else:
        parts.append(
            f"A strategic boost of +{boost} was applied, "
            f"adjusting the score from {base_score:.1f} to {final_score:.1f}."
        )

    return " ".join(parts)
