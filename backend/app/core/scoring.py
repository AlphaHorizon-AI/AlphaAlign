"""
AlphaAlign — Alternative Scoring Engine (Simple Mode).

Applies AHP criteria weights to alternative scores (1-5 scale)
for the three architecture outcomes:
  1. Strong Vendor Commitment
  2. Hybrid AI Operating Model
  3. Independent AI Control Model
"""

from typing import Dict, List

OUTCOMES = ["vendor", "hybrid", "independent"]
OUTCOME_LABELS = {
    "vendor": "Strong Vendor Commitment",
    "hybrid": "Hybrid AI Operating Model",
    "independent": "Independent AI Control Model",
}


def calculate_weighted_scores(
    criteria_weights: Dict[str, float],
    alternative_scores: Dict[str, Dict[str, float]],
) -> Dict[str, float]:
    """
    Calculate weighted scores for each outcome using criteria weights.

    Simple Mode: score = Σ(criterion_weight × alternative_score_for_criterion)

    Scores are on a 1-5 scale per criterion, and weights sum to 1.
    Result is normalized to 0-100 scale.

    Args:
        criteria_weights: {criterion_id: weight} summing to 1.0
        alternative_scores: {criterion_id: {outcome: score}}
            where outcome is 'vendor', 'hybrid', or 'independent'
            and score is 1-5

    Returns:
        {outcome: score_0_to_100}
    """
    outcome_scores = {outcome: 0.0 for outcome in OUTCOMES}

    for criterion_id, weight in criteria_weights.items():
        scores = alternative_scores.get(criterion_id, {})
        for outcome in OUTCOMES:
            raw_score = scores.get(outcome, 3.0)  # Default to 3 (neutral)
            outcome_scores[outcome] += weight * raw_score

    # Normalize from 1-5 scale to 0-100
    # Min possible = 1.0 (all scores = 1), Max possible = 5.0 (all scores = 5)
    for outcome in OUTCOMES:
        raw = outcome_scores[outcome]
        normalized = ((raw - 1.0) / 4.0) * 100.0
        outcome_scores[outcome] = round(max(0, min(100, normalized)), 1)

    return outcome_scores


def aggregate_alternative_scores(
    respondent_scores: Dict[str, List[Dict]],
    respondent_weightings: Dict[str, float] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Aggregate alternative scores from multiple respondents.

    Uses weighted average of scores.

    Args:
        respondent_scores: {respondent_id: [
            {criterion_id, outcome, score}, ...
        ]}
        respondent_weightings: {respondent_id: weight}

    Returns:
        {criterion_id: {outcome: aggregated_score}}
    """
    if not respondent_scores:
        return {}

    respondent_ids = list(respondent_scores.keys())
    if respondent_weightings is None:
        wts = {rid: 1.0 for rid in respondent_ids}
    else:
        wts = respondent_weightings

    total_weight = sum(wts.get(rid, 1.0) for rid in respondent_ids)

    # Collect all scores per (criterion, outcome)
    accumulator: Dict[str, Dict[str, float]] = {}

    for rid in respondent_ids:
        w = wts.get(rid, 1.0) / total_weight
        for entry in respondent_scores[rid]:
            cid = entry["criterion_id"]
            outcome = entry["outcome"]
            score = entry["score"]

            if cid not in accumulator:
                accumulator[cid] = {o: 0.0 for o in OUTCOMES}
            accumulator[cid][outcome] += score * w

    return accumulator


def rank_outcomes(scores: Dict[str, float]) -> List[Dict]:
    """
    Rank outcomes by score and return ordered list.

    Returns:
        List of {outcome, label, score, rank}
    """
    sorted_outcomes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    result = []
    for rank, (outcome, score) in enumerate(sorted_outcomes, 1):
        result.append({
            "outcome": outcome,
            "label": OUTCOME_LABELS.get(outcome, outcome),
            "score": round(score, 1),
            "rank": rank,
        })
    return result
