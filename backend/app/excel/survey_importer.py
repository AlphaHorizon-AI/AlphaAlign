"""
AlphaAlign — Excel Survey Importer.

Parses completed Excel survey files and extracts respondent data,
pairwise comparison values, alternative scores, and comments.
"""

from typing import Dict, List, Tuple, Optional
from openpyxl import load_workbook
import io


def import_survey(file_content: bytes, criteria_map: Dict[str, str]) -> Dict:
    """
    Import a completed survey file.

    Args:
        file_content: Raw bytes of the Excel file.
        criteria_map: {criterion_name: criterion_id} mapping.

    Returns:
        Dict with:
            respondent: {name, role, email}
            pairwise_values: [{criterion_a_id, criterion_b_id, value}]
            alternative_scores: [{criterion_id, outcome, score}]
            strategic_importance: [{item_name, type, value, justification, ...}]
            comments: str
            metadata: {project_id, ...}
    """
    wb = load_workbook(io.BytesIO(file_content), data_only=True)

    respondent = _parse_respondent(wb)
    pairwise = _parse_pairwise(wb, criteria_map)
    alt_scores = _parse_alternative_scores(wb, criteria_map)
    strategic = _parse_strategic_importance(wb)
    comments = _parse_comments(wb)
    metadata = _parse_metadata(wb)

    return {
        "respondent": respondent,
        "pairwise_values": pairwise,
        "alternative_scores": alt_scores,
        "strategic_importance": strategic,
        "comments": comments,
        "metadata": metadata,
    }


def _parse_respondent(wb) -> Dict:
    if "Respondent Profile" not in wb.sheetnames:
        return {"name": "", "role": "", "email": ""}

    ws = wb["Respondent Profile"]
    data = {}
    field_map = {"Name": "name", "Role": "role", "Email": "email"}

    for row in ws.iter_rows(min_row=3, max_row=10, max_col=2, values_only=False):
        if len(row) >= 2 and row[0].value in field_map:
            key = field_map[row[0].value]
            val = row[1].value or ""
            data[key] = str(val).strip()

    return {
        "name": data.get("name", ""),
        "role": data.get("role", ""),
        "email": data.get("email", ""),
    }


def _parse_pairwise(wb, criteria_map: Dict[str, str]) -> List[Dict]:
    if "Pairwise Comparison" not in wb.sheetnames:
        return []

    ws = wb["Pairwise Comparison"]
    results = []

    # Find header row (row 4 by convention)
    header_row = 4
    criteria_cols = {}  # col_index -> criterion_name

    for col in range(2, ws.max_column + 1):
        val = ws.cell(row=header_row, column=col).value
        if val and str(val).strip() in criteria_map:
            criteria_cols[col] = str(val).strip()

    # Read row labels
    criteria_rows = {}  # row_index -> criterion_name
    for row in range(header_row + 1, ws.max_row + 1):
        val = ws.cell(row=row, column=1).value
        if val and str(val).strip() in criteria_map:
            criteria_rows[row] = str(val).strip()

    # Read upper triangle values
    for row_idx, row_name in criteria_rows.items():
        for col_idx, col_name in criteria_cols.items():
            if row_name == col_name:
                continue
            # Only read upper triangle
            row_order = list(criteria_rows.values())
            col_order = list(criteria_cols.values())
            if row_order.index(row_name) >= col_order.index(col_name):
                continue

            cell_value = ws.cell(row=row_idx, column=col_idx).value
            if cell_value is not None:
                try:
                    value = _parse_ahp_value(cell_value)
                    if value is not None and value > 0:
                        results.append({
                            "criterion_a_id": criteria_map[row_name],
                            "criterion_b_id": criteria_map[col_name],
                            "value": value,
                        })
                except (ValueError, ZeroDivisionError):
                    pass

    return results


def _parse_ahp_value(value) -> Optional[float]:
    """Parse an AHP value which could be numeric or a fraction string."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip()
        if "/" in value:
            parts = value.split("/")
            if len(parts) == 2:
                return float(parts[0]) / float(parts[1])
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _parse_alternative_scores(wb, criteria_map: Dict[str, str]) -> List[Dict]:
    if "Alternative Scoring" not in wb.sheetnames:
        return []

    ws = wb["Alternative Scoring"]
    results = []
    outcome_map = {
        "Strong Vendor Commitment": "vendor",
        "Hybrid AI Operating Model": "hybrid",
        "Independent AI Control Model": "independent",
    }

    # Read header row (row 4)
    header_row = 4
    outcome_cols = {}
    for col in range(2, ws.max_column + 1):
        val = ws.cell(row=header_row, column=col).value
        if val and str(val).strip() in outcome_map:
            outcome_cols[col] = outcome_map[str(val).strip()]

    # Read data rows
    for row in range(header_row + 1, ws.max_row + 1):
        criterion_name = ws.cell(row=row, column=1).value
        if not criterion_name or str(criterion_name).strip() not in criteria_map:
            continue

        cid = criteria_map[str(criterion_name).strip()]
        for col_idx, outcome in outcome_cols.items():
            val = ws.cell(row=row, column=col_idx).value
            if val is not None:
                try:
                    score = float(val)
                    score = max(1, min(5, score))  # Clamp to 1-5
                    results.append({
                        "criterion_id": cid,
                        "outcome": outcome,
                        "score": score,
                    })
                except (ValueError, TypeError):
                    pass

    return results


def _parse_strategic_importance(wb) -> List[Dict]:
    if "Strategic Importance" not in wb.sheetnames:
        return []

    ws = wb["Strategic Importance"]
    results = []

    for row in range(5, ws.max_row + 1):
        name = ws.cell(row=row, column=1).value
        if not name:
            continue

        si_value = ws.cell(row=row, column=3).value
        try:
            si = int(si_value) if si_value is not None else 0
        except (ValueError, TypeError):
            si = 0

        results.append({
            "item_name": str(name).strip(),
            "item_type": str(ws.cell(row=row, column=2).value or "outcome").strip(),
            "strategic_importance": max(0, min(10, si)),
            "justification": str(ws.cell(row=row, column=4).value or "").strip(),
            "executive_sponsor": str(ws.cell(row=row, column=5).value or "").strip(),
            "time_horizon": str(ws.cell(row=row, column=6).value or "").strip(),
            "risk_of_not_acting": str(ws.cell(row=row, column=7).value or "").strip(),
        })

    return results


def _parse_comments(wb) -> str:
    if "Comments" not in wb.sheetnames:
        return ""
    ws = wb["Comments"]
    comments = ws.cell(row=5, column=1).value
    return str(comments).strip() if comments else ""


def _parse_metadata(wb) -> Dict:
    if "Metadata" not in wb.sheetnames:
        return {}

    ws = wb["Metadata"]
    data = {}
    for row in range(3, 15):
        key = ws.cell(row=row, column=1).value
        val = ws.cell(row=row, column=2).value
        if key:
            data[str(key).strip()] = str(val).strip() if val else ""

    return data
