"""
AlphaAlign — Recommendation Engine.

Interprets scores, strategic importance, alignment, and readiness
to generate a final recommendation with next-step vs target-state distinction.
"""

from typing import Dict, List, Optional
from app.core.scoring import OUTCOME_LABELS


def generate_recommendation(
    outcome_scores: Dict[str, float],
    final_scores: Dict[str, float],
    criteria_weights: Dict[str, float],
    alignment_data: Dict,
    criterion_names: Dict[str, str],
    project_data: Dict = None,
) -> Dict:
    """
    Generate a full recommendation based on all analysis.

    Args:
        outcome_scores: {outcome: base_ahp_score}
        final_scores: {outcome: final_strategic_score}
        criteria_weights: {criterion_id: weight}
        alignment_data: alignment analysis result
        criterion_names: {criterion_id: name}
        project_data: optional project metadata

    Returns:
        Dict with recommendation, interpretation, next-step, target-state, etc.
    """
    # Rank by final scores
    ranked = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    recommended = ranked[0][0]
    recommended_score = ranked[0][1]

    # Score gaps
    score_gap_1_2 = ranked[0][1] - ranked[1][1] if len(ranked) > 1 else 0
    score_gap_1_3 = ranked[0][1] - ranked[2][1] if len(ranked) > 2 else 0

    # Determine confidence
    if score_gap_1_2 >= 15:
        confidence = "high"
    elif score_gap_1_2 >= 5:
        confidence = "moderate"
    else:
        confidence = "low"

    # Identify top criteria drivers
    top_criteria = sorted(criteria_weights.items(), key=lambda x: x[1], reverse=True)[:5]
    top_drivers = [
        {"criterion_id": cid, "name": criterion_names.get(cid, cid), "weight": round(w, 3)}
        for cid, w in top_criteria
    ]

    # Determine next-step vs target-state
    next_step, target_state, transition_reason = _determine_transition(
        ranked, outcome_scores, criteria_weights, criterion_names
    )

    # Build interpretation text
    interpretation = _build_interpretation(
        recommended, recommended_score, score_gap_1_2,
        confidence, alignment_data, top_drivers
    )

    # Build roadmap suggestion
    roadmap = _suggest_roadmap(recommended, target_state)

    return {
        "recommended_outcome": recommended,
        "recommended_label": OUTCOME_LABELS.get(recommended, recommended),
        "recommended_score": round(recommended_score, 1),
        "confidence": confidence,
        "score_gap": round(score_gap_1_2, 1),
        "outcome_ranking": [
            {
                "outcome": o,
                "label": OUTCOME_LABELS.get(o, o),
                "base_score": round(outcome_scores.get(o, 0), 1),
                "final_score": round(final_scores.get(o, 0), 1),
            }
            for o, _ in ranked
        ],
        "top_drivers": top_drivers,
        "next_step": {
            "outcome": next_step,
            "label": OUTCOME_LABELS.get(next_step, next_step),
        },
        "target_state": {
            "outcome": target_state,
            "label": OUTCOME_LABELS.get(target_state, target_state),
        },
        "transition_reason": transition_reason,
        "interpretation": interpretation,
        "roadmap": roadmap,
        "alignment_summary": alignment_data.get("summary", ""),
    }


def _determine_transition(ranked, base_scores, criteria_weights, criterion_names):
    """Distinguish between recommended next step and long-term target."""
    top_outcome = ranked[0][0]
    top_score = ranked[0][1]

    # Check if "independent" scores high strategically but readiness is low
    # Find the "Internal Capability Readiness" criterion
    readiness_cid = None
    readiness_weight = 0.0
    for cid, name in criterion_names.items():
        if "readiness" in name.lower() or "capability" in name.lower():
            readiness_cid = cid
            readiness_weight = criteria_weights.get(cid, 0)
            break

    # If independent is the top pick, it's both next step and target
    if top_outcome == "independent":
        # Check if readiness is very low (weight < 5%)
        if readiness_weight < 0.05:
            return "hybrid", "independent", (
                "Independent AI Control scores highest strategically, but internal "
                "readiness may not yet be strong enough. A hybrid approach is "
                "recommended as the next step, with independence as the long-term target."
            )
        return "independent", "independent", "Independent AI Control is both the recommended next step and target state."

    if top_outcome == "hybrid":
        # Check if independent is close behind
        ind_score = next((s for o, s in ranked if o == "independent"), 0)
        if ind_score > 0 and top_score - ind_score < 10:
            return "hybrid", "independent", (
                "Hybrid is the recommended next step. Independent AI Control scores "
                "closely behind and represents a strong long-term target state."
            )
        return "hybrid", "hybrid", "Hybrid AI Operating Model is both the recommended next step and target state."

    # Vendor commitment
    return "vendor", top_outcome, (
        "Strong Vendor Commitment is the recommended current approach. "
        "As AI maturity grows, the company should reassess the architecture posture."
    )


def _build_interpretation(recommended, score, gap, confidence, alignment_data, top_drivers):
    """Build human-readable interpretation text."""
    label = OUTCOME_LABELS.get(recommended, recommended)
    parts = [f"Recommended position: {label} (score: {score:.0f}/100)."]

    if confidence == "high":
        parts.append(f"This recommendation has high confidence with a {gap:.0f}-point lead over the next option.")
    elif confidence == "moderate":
        parts.append(f"This recommendation has moderate confidence ({gap:.0f}-point gap). Consider reviewing the scoring inputs.")
    else:
        parts.append(f"The scores are close ({gap:.0f}-point gap), suggesting the decision requires careful deliberation.")

    if top_drivers:
        driver_names = [d["name"] for d in top_drivers[:3]]
        parts.append(f"The top decision drivers are: {', '.join(driver_names)}.")

    alignment_summary = alignment_data.get("summary", "")
    if alignment_summary:
        parts.append(alignment_summary)

    return " ".join(parts)


def _suggest_roadmap(next_step, target_state):
    """Suggest a phased roadmap based on the recommendation."""
    roadmaps = {
        "vendor": [
            {"phase": "0–3 months", "focus": "Confirm vendor ecosystem strategy and standardize AI tooling"},
            {"phase": "3–6 months", "focus": "Deploy vendor AI capabilities across priority use cases"},
            {"phase": "6–12 months", "focus": "Establish governance framework within vendor ecosystem"},
            {"phase": "12–24 months", "focus": "Reassess architecture posture as AI needs evolve"},
        ],
        "hybrid": [
            {"phase": "0–3 months", "focus": "Confirm AI operating model and governance structure"},
            {"phase": "3–6 months", "focus": "Pilot hybrid orchestration for selected use cases"},
            {"phase": "6–12 months", "focus": "Build portfolio governance and model selection process"},
            {"phase": "12–24 months", "focus": "Expand independent control for business-critical AI workflows"},
        ],
        "independent": [
            {"phase": "0–3 months", "focus": "Design independent AI orchestration architecture"},
            {"phase": "3–6 months", "focus": "Build foundation platform and model-agnostic execution layer"},
            {"phase": "6–12 months", "focus": "Migrate strategic workflows to independent control"},
            {"phase": "12–24 months", "focus": "Full vendor-agnostic AI operations with enterprise governance"},
        ],
    }
    return roadmaps.get(next_step, roadmaps["hybrid"])
