"""
AlphaAlign — Excel Survey Template Generator.

Generates professional Excel survey templates with:
  1. Instructions tab
  2. Respondent Profile tab
  3. Pairwise Comparison tab
  4. Alternative Scoring tab
  5. Strategic Importance tab
  6. Comments tab
  7. Metadata tab
"""

import io
from datetime import datetime
from typing import List, Dict

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation


# ── Style constants ──
HEADER_FONT = Font(name="Calibri", bold=True, color="FFFFFF", size=12)
HEADER_FILL = PatternFill(start_color="1a237e", end_color="1a237e", fill_type="solid")
SUB_HEADER_FILL = PatternFill(start_color="283593", end_color="283593", fill_type="solid")
LABEL_FONT = Font(name="Calibri", bold=True, size=11)
BODY_FONT = Font(name="Calibri", size=11)
LIGHT_FILL = PatternFill(start_color="e8eaf6", end_color="e8eaf6", fill_type="solid")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT_WRAP = Alignment(horizontal="left", vertical="top", wrap_text=True)
THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)


def generate_survey_template(
    project_id: str,
    project_name: str,
    company_name: str,
    criteria: List[Dict],
    include_strategic_importance: bool = True,
) -> io.BytesIO:
    """
    Generate an Excel survey template file.

    Args:
        project_id: Project UUID.
        project_name: Assessment name.
        company_name: Company name.
        criteria: List of {id, name, description}.
        include_strategic_importance: Whether to include SI tab.

    Returns:
        BytesIO buffer containing the Excel file.
    """
    wb = Workbook()

    _create_instructions_tab(wb, project_name, company_name, criteria)
    _create_respondent_profile_tab(wb)
    _create_pairwise_tab(wb, criteria)
    _create_alternative_scoring_tab(wb, criteria)
    if include_strategic_importance:
        _create_strategic_importance_tab(wb)
    _create_comments_tab(wb)
    _create_metadata_tab(wb, project_id, project_name, company_name, criteria)

    # Remove default sheet
    if "Sheet" in wb.sheetnames:
        del wb["Sheet"]

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def _style_header_row(ws, row, max_col):
    for col in range(1, max_col + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = CENTER
        cell.border = THIN_BORDER


def _create_instructions_tab(wb, project_name, company_name, criteria):
    ws = wb.create_sheet("Instructions")
    ws.sheet_properties.tabColor = "1a237e"
    ws.column_dimensions["A"].width = 80

    instructions = [
        f"AlphaAlign — Strategic AI Choice Assessment",
        f"",
        f"Assessment: {project_name}",
        f"Company: {company_name}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"INSTRUCTIONS",
        f"",
        f"This survey is part of a structured decision-support assessment to determine",
        f"the optimal AI architecture posture for your organization.",
        f"",
        f"Please complete the following tabs:",
        f"",
        f"1. RESPONDENT PROFILE — Enter your name, role, and email.",
        f"",
        f"2. PAIRWISE COMPARISON — Compare each pair of criteria.",
        f"   For each pair, indicate which criterion is more important and by how much.",
        f"   Use the Saaty scale (1-9):",
        f"     1 = Equal importance",
        f"     3 = Moderate importance",
        f"     5 = Strong importance",
        f"     7 = Very strong importance",
        f"     9 = Extreme importance",
        f"   Use 2, 4, 6, 8 for intermediate values.",
        f"   Enter values > 1 if Criterion A is more important.",
        f"   Enter fractions (1/3, 1/5, etc.) if Criterion B is more important.",
        f"",
        f"3. ALTERNATIVE SCORING — Rate each AI architecture outcome (1-5)",
        f"   against each criterion.",
        f"     1 = Very poor fit",
        f"     2 = Poor fit",
        f"     3 = Neutral / moderate fit",
        f"     4 = Good fit",
        f"     5 = Excellent fit",
        f"",
        f"4. STRATEGIC IMPORTANCE (Optional) — Rate the strategic importance",
        f"   of specific outcomes or initiatives (0-10 scale).",
        f"",
        f"5. COMMENTS — Add any free-text observations or concerns.",
        f"",
        f"CRITERIA BEING EVALUATED:",
        f"",
    ]

    for i, c in enumerate(criteria, 1):
        instructions.append(f"  {i}. {c['name']}: {c.get('description', '')}")

    for i, text in enumerate(instructions, 1):
        cell = ws.cell(row=i, column=1, value=text)
        cell.font = Font(name="Calibri", size=11, bold=(i in [1, 7, 39]))
        if i == 1:
            cell.font = Font(name="Calibri", size=16, bold=True, color="1a237e")


def _create_respondent_profile_tab(wb):
    ws = wb.create_sheet("Respondent Profile")
    ws.sheet_properties.tabColor = "283593"
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 40

    fields = [
        ("Name", "Enter your full name"),
        ("Role", "e.g. CEO, CFO, CIO, CTO, CISO, COO, CHRO, Business Unit Leader"),
        ("Email", "Enter your email address"),
        ("Department", "Enter your department (optional)"),
        ("Date", datetime.now().strftime("%Y-%m-%d")),
    ]

    ws.cell(row=1, column=1, value="Respondent Profile")
    ws.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color="1a237e")

    for i, (label, value) in enumerate(fields, 3):
        cell_a = ws.cell(row=i, column=1, value=label)
        cell_a.font = LABEL_FONT
        cell_a.border = THIN_BORDER
        cell_a.fill = LIGHT_FILL

        cell_b = ws.cell(row=i, column=2, value=value if label == "Date" else "")
        cell_b.font = BODY_FONT
        cell_b.border = THIN_BORDER
        if label != "Date":
            cell_b.font = Font(name="Calibri", size=11, color="999999")


def _create_pairwise_tab(wb, criteria):
    ws = wb.create_sheet("Pairwise Comparison")
    ws.sheet_properties.tabColor = "3949ab"

    n = len(criteria)

    # Title
    ws.cell(row=1, column=1, value="Pairwise Comparison Matrix")
    ws.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color="1a237e")

    ws.cell(row=2, column=1, value="Compare criteria: if A is more important, enter 1-9. If B is more important, enter the reciprocal (e.g. 1/3, 1/5).")
    ws.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True)

    start_row = 4

    # Header row
    ws.column_dimensions["A"].width = 30
    ws.cell(row=start_row, column=1, value="Criterion A ↓ / Criterion B →")
    ws.cell(row=start_row, column=1).font = HEADER_FONT
    ws.cell(row=start_row, column=1).fill = HEADER_FILL
    ws.cell(row=start_row, column=1).border = THIN_BORDER

    for j, c in enumerate(criteria):
        col = j + 2
        ws.column_dimensions[get_column_letter(col)].width = 18
        cell = ws.cell(row=start_row, column=col, value=c["name"])
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = CENTER
        cell.border = THIN_BORDER

    # Matrix rows
    for i, c_row in enumerate(criteria):
        row = start_row + 1 + i
        cell = ws.cell(row=row, column=1, value=c_row["name"])
        cell.font = LABEL_FONT
        cell.fill = LIGHT_FILL
        cell.border = THIN_BORDER

        for j, c_col in enumerate(criteria):
            col = j + 2
            cell = ws.cell(row=row, column=col)
            cell.border = THIN_BORDER
            cell.alignment = CENTER

            if i == j:
                cell.value = 1
                cell.fill = PatternFill(start_color="c5cae9", end_color="c5cae9", fill_type="solid")
                cell.font = Font(name="Calibri", size=11, color="666666")
            elif i < j:
                # Upper triangle — user fills these
                cell.fill = PatternFill(start_color="ffffff", end_color="ffffff", fill_type="solid")
                cell.font = BODY_FONT
            else:
                # Lower triangle — auto-calculated (reciprocal)
                cell.fill = PatternFill(start_color="e8eaf6", end_color="e8eaf6", fill_type="solid")
                cell.font = Font(name="Calibri", size=11, color="999999")
                # Formula to compute reciprocal
                upper_cell = ws.cell(row=start_row + 1 + j, column=i + 2)
                upper_ref = f"{get_column_letter(i + 2)}{start_row + 1 + j}"
                cell.value = f"=IF({upper_ref}=0, 1, 1/{upper_ref})"


def _create_alternative_scoring_tab(wb, criteria):
    ws = wb.create_sheet("Alternative Scoring")
    ws.sheet_properties.tabColor = "5c6bc0"

    outcomes = [
        "Strong Vendor Commitment",
        "Hybrid AI Operating Model",
        "Independent AI Control Model",
    ]

    ws.cell(row=1, column=1, value="Alternative Scoring")
    ws.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color="1a237e")
    ws.cell(row=2, column=1, value="Rate each architecture outcome against each criterion (1 = Very poor fit, 5 = Excellent fit).")
    ws.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True)

    start_row = 4
    ws.column_dimensions["A"].width = 30

    # Header
    ws.cell(row=start_row, column=1, value="Criterion")
    ws.cell(row=start_row, column=1).font = HEADER_FONT
    ws.cell(row=start_row, column=1).fill = HEADER_FILL
    ws.cell(row=start_row, column=1).border = THIN_BORDER

    for j, outcome in enumerate(outcomes):
        col = j + 2
        ws.column_dimensions[get_column_letter(col)].width = 28
        cell = ws.cell(row=start_row, column=col, value=outcome)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = CENTER
        cell.border = THIN_BORDER

    # Data validation: 1-5
    dv = DataValidation(type="whole", operator="between", formula1="1", formula2="5")
    dv.error = "Please enter a value between 1 and 5"
    dv.errorTitle = "Invalid Score"
    ws.add_data_validation(dv)

    # Rows
    for i, c in enumerate(criteria):
        row = start_row + 1 + i
        cell = ws.cell(row=row, column=1, value=c["name"])
        cell.font = LABEL_FONT
        cell.fill = LIGHT_FILL
        cell.border = THIN_BORDER

        for j in range(3):
            col = j + 2
            cell = ws.cell(row=row, column=col)
            cell.border = THIN_BORDER
            cell.alignment = CENTER
            dv.add(cell)


def _create_strategic_importance_tab(wb):
    ws = wb.create_sheet("Strategic Importance")
    ws.sheet_properties.tabColor = "7986cb"

    ws.cell(row=1, column=1, value="Strategic Importance Appendix")
    ws.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color="1a237e")
    ws.cell(row=2, column=1, value="Rate the strategic importance of outcomes or initiatives (0 = No override, 10 = Critical imperative). Justification required for values ≥ 7.")
    ws.cell(row=2, column=1).font = Font(name="Calibri", size=10, italic=True)

    headers = ["Item Name", "Type", "Strategic Importance (0-10)", "Justification",
               "Executive Sponsor", "Time Horizon", "Risk of Not Acting"]
    widths = [30, 15, 25, 40, 20, 15, 30]

    for j, (h, w) in enumerate(zip(headers, widths)):
        col = j + 1
        ws.column_dimensions[get_column_letter(col)].width = w
        cell = ws.cell(row=4, column=col, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = CENTER
        cell.border = THIN_BORDER

    # Pre-fill with 3 outcome rows
    outcomes = ["Strong Vendor Commitment", "Hybrid AI Operating Model", "Independent AI Control Model"]
    for i, outcome in enumerate(outcomes):
        row = 5 + i
        ws.cell(row=row, column=1, value=outcome).border = THIN_BORDER
        ws.cell(row=row, column=2, value="outcome").border = THIN_BORDER
        for j in range(3, 8):
            ws.cell(row=row, column=j).border = THIN_BORDER


def _create_comments_tab(wb):
    ws = wb.create_sheet("Comments")
    ws.sheet_properties.tabColor = "9fa8da"
    ws.column_dimensions["A"].width = 80

    ws.cell(row=1, column=1, value="Comments and Observations")
    ws.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color="1a237e")
    ws.cell(row=3, column=1, value="Please enter any additional observations, concerns, or strategic context below:")
    ws.cell(row=3, column=1).font = BODY_FONT
    ws.cell(row=5, column=1).border = THIN_BORDER
    ws.row_dimensions[5].height = 200


def _create_metadata_tab(wb, project_id, project_name, company_name, criteria):
    ws = wb.create_sheet("Metadata")
    ws.sheet_properties.tabColor = "c5cae9"
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 50

    metadata = [
        ("Project ID", project_id),
        ("Project Name", project_name),
        ("Company Name", company_name),
        ("Generated At", datetime.now().isoformat()),
        ("Criteria Count", str(len(criteria))),
        ("Version", "1.0"),
        ("Application", "AlphaAlign"),
    ]

    ws.cell(row=1, column=1, value="Metadata (Do Not Edit)")
    ws.cell(row=1, column=1).font = Font(name="Calibri", size=14, bold=True, color="FF0000")

    for i, (key, value) in enumerate(metadata, 3):
        ws.cell(row=i, column=1, value=key).font = LABEL_FONT
        ws.cell(row=i, column=2, value=value).font = BODY_FONT

    # Criteria list
    row = 3 + len(metadata) + 1
    ws.cell(row=row, column=1, value="Criteria").font = LABEL_FONT
    for i, c in enumerate(criteria):
        ws.cell(row=row + 1 + i, column=1, value=c["id"]).font = Font(name="Calibri", size=9)
        ws.cell(row=row + 1 + i, column=2, value=c["name"]).font = BODY_FONT
