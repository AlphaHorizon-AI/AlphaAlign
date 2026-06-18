"""
AlphaAlign — Leadership Alignment Analysis.

Analyzes whether the leadership team is aligned or divided
on each criterion. Identifies areas of agreement, disagreement,
outliers, and role-based differences.
"""

import numpy as np
from typing import Dict, List, Optional


def calculate_alignment(
    respondent_weights: Dict[str, Dict[str, float]],
    respondent_roles: Dict[str, str],
    criterion_names: Dict[str, str],
) -> Dict:
    """
    Analyze leadership alignment across all criteria.

    Args:
        respondent_weights: {respondent_id: {criterion_id: weight}}
        respondent_roles: {respondent_id: role}
        criterion_names: {criterion_id: name}

    Returns:
        Dict with:
            criteria_alignment: [{criterion_id, name, alignment_level, std_dev, mean, values}]
            strong_alignment: [criterion_ids with strong alignment]
            mixed_alignment: [criterion_ids with mixed alignment]
            low_alignment: [criterion_ids with low alignment]
            outlier_respondents: [{respondent_id, criterion_id, deviation}]
            role_differences: [{criterion_id, role_groups}]
            summary: text summary
    """
    if not respondent_weights:
        return _empty_result()

    respondent_ids = list(respondent_weights.keys())
    criterion_ids = list(next(iter(respondent_weights.values())).keys())

    criteria_alignment = []
    strong = []
    mixed = []
    low = []
    outliers = []

    for cid in criterion_ids:
        values = [respondent_weights[rid].get(cid, 0) for rid in respondent_ids]
        arr = np.array(values)

        mean = float(np.mean(arr))
        std = float(np.std(arr))

        # Coefficient of variation for alignment classification
        cv = std / mean if mean > 0 else 0

        if cv <= 0.15:
            level = "strong"
            strong.append(cid)
        elif cv <= 0.35:
            level = "mixed"
            mixed.append(cid)
        else:
            level = "low"
            low.append(cid)

        # Detect outliers (> 2 standard deviations from mean)
        for i, rid in enumerate(respondent_ids):
            if std > 0 and abs(values[i] - mean) > 2 * std:
                outliers.append({
                    "respondent_id": rid,
                    "criterion_id": cid,
                    "criterion_name": criterion_names.get(cid, cid),
                    "value": round(values[i], 4),
                    "mean": round(mean, 4),
                    "deviation": round(abs(values[i] - mean) / std, 2),
                })

        criteria_alignment.append({
            "criterion_id": cid,
            "name": criterion_names.get(cid, cid),
            "alignment_level": level,
            "std_dev": round(std, 4),
            "mean": round(mean, 4),
            "cv": round(cv, 4),
            "values": {rid: round(v, 4) for rid, v in zip(respondent_ids, values)},
        })

    # Role-based differences
    role_diffs = _analyze_role_differences(respondent_weights, respondent_roles, criterion_ids, criterion_names)

    summary = _build_alignment_summary(
        criteria_alignment, strong, mixed, low, outliers, criterion_names
    )

    return {
        "criteria_alignment": criteria_alignment,
        "strong_alignment": strong,
        "mixed_alignment": mixed,
        "low_alignment": low,
        "outlier_respondents": outliers,
        "role_differences": role_diffs,
        "summary": summary,
    }


def _analyze_role_differences(
    respondent_weights: Dict[str, Dict[str, float]],
    respondent_roles: Dict[str, str],
    criterion_ids: List[str],
    criterion_names: Dict[str, str],
) -> List[Dict]:
    """Analyze weight differences grouped by role."""
    # Group respondents by role
    role_groups: Dict[str, List[str]] = {}
    for rid, role in respondent_roles.items():
        if role not in role_groups:
            role_groups[role] = []
        role_groups[role].append(rid)

    if len(role_groups) < 2:
        return []

    results = []
    for cid in criterion_ids:
        role_means = {}
        for role, rids in role_groups.items():
            values = [respondent_weights.get(rid, {}).get(cid, 0) for rid in rids]
            role_means[role] = round(float(np.mean(values)), 4) if values else 0

        # Check if there's meaningful difference between roles
        mean_values = list(role_means.values())
        if len(mean_values) >= 2 and max(mean_values) > 0:
            spread = max(mean_values) - min(mean_values)
            avg = np.mean(mean_values)
            if avg > 0 and spread / avg > 0.3:  # >30% spread
                results.append({
                    "criterion_id": cid,
                    "criterion_name": criterion_names.get(cid, cid),
                    "role_means": role_means,
                    "spread": round(spread, 4),
                })

    return results


def _build_alignment_summary(
    criteria_alignment, strong, mixed, low, outliers, criterion_names
) -> str:
    """Build a human-readable alignment summary."""
    parts = []

    if strong:
        names = [criterion_names.get(cid, cid) for cid in strong[:3]]
        parts.append(f"The leadership team is aligned on {', '.join(names)}.")

    if low:
        names = [criterion_names.get(cid, cid) for cid in low[:3]]
        parts.append(f"Significant disagreement exists on {', '.join(names)}.")

    if mixed:
        parts.append(f"{len(mixed)} criteria show mixed alignment and may benefit from further discussion.")

    if outliers:
        parts.append(f"{len(outliers)} outlier response(s) detected that diverge significantly from the group.")

    if not parts:
        parts.append("Insufficient data for alignment analysis.")

    return " ".join(parts)


def _empty_result():
    return {
        "criteria_alignment": [],
        "strong_alignment": [],
        "mixed_alignment": [],
        "low_alignment": [],
        "outlier_respondents": [],
        "role_differences": [],
        "summary": "No respondent data available for alignment analysis.",
    }
