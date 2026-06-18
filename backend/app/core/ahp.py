"""
AlphaAlign — AHP (Analytic Hierarchy Process) Calculation Engine.

Implements the geometric mean method for priority vector calculation
from pairwise comparison matrices.
"""

import numpy as np
from typing import Dict, List, Tuple


def build_comparison_matrix(
    criteria_ids: List[str],
    pairwise_values: List[Dict],
) -> np.ndarray:
    """
    Build an n×n pairwise comparison matrix from respondent data.

    Args:
        criteria_ids: Ordered list of criterion IDs.
        pairwise_values: List of dicts with keys:
            criterion_a_id, criterion_b_id, value

    Returns:
        n×n numpy array where M[i][j] = importance of criterion i over j.
    """
    n = len(criteria_ids)
    matrix = np.ones((n, n))
    id_to_idx = {cid: i for i, cid in enumerate(criteria_ids)}

    for pv in pairwise_values:
        a_idx = id_to_idx.get(pv["criterion_a_id"])
        b_idx = id_to_idx.get(pv["criterion_b_id"])
        if a_idx is not None and b_idx is not None:
            val = pv["value"]
            matrix[a_idx][b_idx] = val
            matrix[b_idx][a_idx] = 1.0 / val if val != 0 else 1.0

    return matrix


def calculate_weights_geometric_mean(matrix: np.ndarray) -> np.ndarray:
    """
    Calculate priority vector using the geometric mean method.

    For each row, compute the geometric mean of all elements,
    then normalize so weights sum to 1.

    Args:
        matrix: n×n pairwise comparison matrix.

    Returns:
        Array of n weights summing to 1.0.
    """
    n = matrix.shape[0]
    # Geometric mean of each row
    geo_means = np.prod(matrix, axis=1) ** (1.0 / n)
    # Normalize
    total = geo_means.sum()
    if total == 0:
        return np.ones(n) / n
    weights = geo_means / total
    return weights


def calculate_lambda_max(matrix: np.ndarray, weights: np.ndarray) -> float:
    """
    Calculate λ_max (principal eigenvalue approximation).

    λ_max = sum of (weighted column sums).
    """
    n = matrix.shape[0]
    # Multiply matrix by weight vector
    Aw = matrix @ weights
    # λ_max = average of Aw[i] / w[i]
    ratios = Aw / weights
    lambda_max = np.mean(ratios)
    return float(lambda_max)


def calculate_ahp(
    criteria_ids: List[str],
    pairwise_values: List[Dict],
) -> Dict:
    """
    Full AHP calculation for one respondent.

    Returns:
        Dict with keys:
            weights: {criterion_id: weight}
            matrix: the comparison matrix as nested list
            lambda_max: principal eigenvalue
            ci: consistency index
            cr: consistency ratio
            consistency_status: 'good' | 'acceptable' | 'inconsistent'
    """
    from app.core.consistency import calculate_consistency_ratio, interpret_consistency

    matrix = build_comparison_matrix(criteria_ids, pairwise_values)
    weights = calculate_weights_geometric_mean(matrix)
    lambda_max = calculate_lambda_max(matrix, weights)

    n = len(criteria_ids)
    ci, cr = calculate_consistency_ratio(lambda_max, n)
    status = interpret_consistency(cr)

    weight_dict = {cid: float(w) for cid, w in zip(criteria_ids, weights)}

    return {
        "weights": weight_dict,
        "matrix": matrix.tolist(),
        "lambda_max": round(lambda_max, 4),
        "ci": round(ci, 4),
        "cr": round(cr, 4),
        "consistency_status": status,
    }
