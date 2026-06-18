"""
AlphaAlign — Survey Validation Engine.

Validates uploaded Excel survey files for completeness and correctness.
"""

from typing import Dict, List


def validate_survey(
    survey_data: Dict,
    criteria_ids: List[str],
    existing_respondent_names: List[str] = None,
) -> Dict:
    """
    Validate a parsed survey file.

    Args:
        survey_data: Parsed survey data from import_survey().
        criteria_ids: List of expected criterion IDs for the project.
        existing_respondent_names: Names already uploaded (for duplicate check).

    Returns:
        Dict with:
            valid: bool
            errors: list of error messages
            warnings: list of warning messages
    """
    errors = []
    warnings = []

    # 1. Validate respondent profile
    respondent = survey_data.get("respondent", {})
    if not respondent.get("name"):
        errors.append("Respondent name is missing in the Respondent Profile tab.")
    if not respondent.get("role"):
        warnings.append("Respondent role is not specified. Role-based weighting will not be available.")

    # Check duplicate respondent
    if existing_respondent_names and respondent.get("name") in existing_respondent_names:
        errors.append(f"A respondent named '{respondent['name']}' has already been uploaded.")

    # 2. Validate pairwise comparisons
    pairwise = survey_data.get("pairwise_values", [])
    n = len(criteria_ids)
    expected_pairs = n * (n - 1) // 2

    if len(pairwise) == 0:
        errors.append("No pairwise comparison values found. The Pairwise Comparison tab may be empty.")
    elif len(pairwise) < expected_pairs:
        missing = expected_pairs - len(pairwise)
        errors.append(
            f"Missing {missing} pairwise comparison(s). "
            f"Expected {expected_pairs}, found {len(pairwise)}."
        )

    # Validate pairwise values are in valid AHP range
    for pv in pairwise:
        val = pv.get("value", 0)
        if val <= 0:
            errors.append(f"Invalid pairwise value ({val}). Values must be positive.")
        elif val > 9:
            warnings.append(f"Pairwise value {val} exceeds the standard Saaty scale (1-9).")
        # Check that criteria IDs match project criteria
        for key in ["criterion_a_id", "criterion_b_id"]:
            cid = pv.get(key, "")
            if cid and cid not in criteria_ids:
                errors.append(f"Pairwise comparison references unknown criterion ID: {cid}")

    # 3. Validate alternative scores
    alt_scores = survey_data.get("alternative_scores", [])
    valid_outcomes = {"vendor", "hybrid", "independent"}

    if len(alt_scores) == 0:
        warnings.append("No alternative scores found. The Alternative Scoring tab may be empty.")
    else:
        expected_scores = n * 3  # 3 outcomes per criterion
        if len(alt_scores) < expected_scores:
            missing = expected_scores - len(alt_scores)
            warnings.append(f"Missing {missing} alternative score(s). Some criteria may not have scores for all outcomes.")

        for score in alt_scores:
            if score.get("outcome") not in valid_outcomes:
                errors.append(f"Invalid outcome '{score.get('outcome')}'. Must be vendor, hybrid, or independent.")
            val = score.get("score", 0)
            if val < 1 or val > 5:
                errors.append(f"Alternative score {val} is out of range. Must be 1-5.")
            if score.get("criterion_id") not in criteria_ids:
                errors.append(f"Alternative score references unknown criterion ID: {score.get('criterion_id')}")

    # 4. Validate strategic importance
    strategic = survey_data.get("strategic_importance", [])
    for si in strategic:
        val = si.get("strategic_importance", 0)
        if val < 0 or val > 10:
            errors.append(f"Strategic importance value {val} is out of range for '{si.get('item_name', '')}'. Must be 0-10.")
        if val >= 7 and not si.get("justification"):
            warnings.append(
                f"Strategic importance is {val} for '{si.get('item_name', '')}' "
                f"but no justification is provided. Justification is recommended for values ≥ 7."
            )

    # 5. Check metadata
    metadata = survey_data.get("metadata", {})
    if not metadata.get("Project ID"):
        warnings.append("No Project ID found in metadata. File may not match this project.")

    is_valid = len(errors) == 0
    return {
        "valid": is_valid,
        "errors": errors,
        "warnings": warnings,
    }
