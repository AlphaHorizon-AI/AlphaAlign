"""
AlphaAlign — Leadership Response Aggregation.

Supports three aggregation modes:
  1. Equal weighting (geometric mean of all respondent matrices)
  2. Role-based weighting (default role weights)
  3. Custom per-respondent weighting
"""

import numpy as np
from typing import Dict, List


def aggregate_matrices_geometric_mean(
    matrices: List[np.ndarray],
    weights: List[float] = None,
) -> np.ndarray:
    """
    Aggregate multiple pairwise comparison matrices using
    weighted geometric mean.

    For equal weighting, each matrix contributes equally.
    For weighted aggregation, each matrix is raised to
    its normalized weight power before multiplication.

    Args:
        matrices: List of n×n pairwise comparison matrices.
        weights: Optional list of respondent weights.

    Returns:
        Aggregated n×n matrix.
    """
    if not matrices:
        raise ValueError("No matrices to aggregate")

    if len(matrices) == 1:
        return matrices[0]

    n = matrices[0].shape[0]
    k = len(matrices)

    if weights is None:
        # Equal weighting: simple geometric mean
        weights = [1.0] * k

    # Normalize weights to sum to 1
    total_weight = sum(weights)
    norm_weights = [w / total_weight for w in weights]

    # Weighted geometric mean element-wise
    aggregated = np.ones((n, n))
    for i in range(n):
        for j in range(n):
            product = 1.0
            for m_idx, matrix in enumerate(matrices):
                product *= matrix[i][j] ** norm_weights[m_idx]
            aggregated[i][j] = product

    return aggregated


def aggregate_weights(
    respondent_weights: Dict[str, Dict[str, float]],
    respondent_weightings: Dict[str, float] = None,
) -> Dict[str, float]:
    """
    Aggregate individual respondent criteria weights into group weights.

    Uses weighted geometric mean of individual weights.

    Args:
        respondent_weights: {respondent_id: {criterion_id: weight}}
        respondent_weightings: {respondent_id: weighting_factor}

    Returns:
        {criterion_id: aggregated_weight}
    """
    if not respondent_weights:
        return {}

    respondent_ids = list(respondent_weights.keys())
    if not respondent_ids:
        return {}

    # Get all criterion IDs from first respondent
    criterion_ids = list(respondent_weights[respondent_ids[0]].keys())

    if respondent_weightings is None:
        wts = [1.0] * len(respondent_ids)
    else:
        wts = [respondent_weightings.get(rid, 1.0) for rid in respondent_ids]

    # Normalize weights
    total = sum(wts)
    norm_wts = [w / total for w in wts]

    aggregated = {}
    for cid in criterion_ids:
        # Weighted geometric mean
        product = 1.0
        for i, rid in enumerate(respondent_ids):
            val = respondent_weights[rid].get(cid, 0.0)
            if val > 0:
                product *= val ** norm_wts[i]
        aggregated[cid] = product

    # Renormalize to sum to 1
    total = sum(aggregated.values())
    if total > 0:
        aggregated = {k: v / total for k, v in aggregated.items()}

    return aggregated
