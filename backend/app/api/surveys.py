"""
AlphaAlign — Survey template generation and upload endpoints.
"""

import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.db.models import (
    Project, Criterion, Respondent, PairwiseResponse,
    AlternativeScore, generate_uuid
)
from app.excel.template_generator import generate_survey_template, get_file_extension
from app.excel.survey_importer import import_survey
from app.excel.validator import validate_survey

router = APIRouter()

UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "uploads"


@router.post("/projects/{project_id}/generate-survey-template")
async def generate_template(project_id: str, session: AsyncSession = Depends(get_session)):
    """Generate and download an Excel survey template."""
    # Get project
    result = await session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")

    # Get criteria
    result = await session.execute(
        select(Criterion)
        .where(Criterion.project_id == project_id, Criterion.active == True)
        .order_by(Criterion.sort_order)
    )
    criteria = result.scalars().all()
    if not criteria:
        raise HTTPException(400, "No criteria defined. Add criteria before generating the survey template.")

    criteria_list = [{"id": c.id, "name": c.name, "description": c.description} for c in criteria]

    buffer = generate_survey_template(
        project_id=project.id,
        project_name=project.name,
        company_name=project.company_name,
        criteria=criteria_list,
    )

    ext = get_file_extension(buffer)
    safe_company = project.company_name.replace(' ', '_').replace('"', '')
    filename = f"AlphaAlign_Survey_{safe_company}{ext}"

    if ext == ".xlsm":
        mime = "application/vnd.ms-excel.sheet.macroEnabled.12"
    else:
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return StreamingResponse(
        buffer,
        media_type=mime,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/projects/{project_id}/upload-survey")
async def upload_survey(
    project_id: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    """Upload and process a completed survey file."""
    # Validate file type
    if not file.filename.endswith((".xlsx", ".xlsm")):
        raise HTTPException(400, "File must be an Excel file (.xlsx)")

    # Get project criteria
    result = await session.execute(
        select(Criterion)
        .where(Criterion.project_id == project_id, Criterion.active == True)
        .order_by(Criterion.sort_order)
    )
    criteria = result.scalars().all()
    criteria_map = {c.name: c.id for c in criteria}
    criteria_ids = [c.id for c in criteria]

    # Get existing respondent names for duplicate check
    result = await session.execute(
        select(Respondent.name).where(Respondent.project_id == project_id)
    )
    existing_names = [r[0] for r in result.all()]

    # Read and parse the file
    content = await file.read()

    # Save file to uploads
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    upload_path = UPLOADS_DIR / f"{project_id}_{file.filename}"
    with open(upload_path, "wb") as f:
        f.write(content)

    # Import and validate
    try:
        survey_data = import_survey(content, criteria_map)
    except Exception as e:
        raise HTTPException(400, f"Failed to parse survey file: {str(e)}")

    validation = validate_survey(survey_data, criteria_ids, existing_names)

    if not validation["valid"]:
        return {
            "status": "invalid",
            "errors": validation["errors"],
            "warnings": validation["warnings"],
            "respondent": survey_data.get("respondent", {}),
        }

    # Create respondent
    resp_data = survey_data["respondent"]
    respondent = Respondent(
        id=generate_uuid(),
        project_id=project_id,
        name=resp_data.get("name", "Unknown"),
        role=resp_data.get("role", ""),
        email=resp_data.get("email", ""),
        imported_from_file=file.filename,
        comments=survey_data.get("comments", ""),
        upload_status="valid",
    )
    session.add(respondent)

    # Save pairwise responses
    for pv in survey_data.get("pairwise_values", []):
        pw = PairwiseResponse(
            id=generate_uuid(),
            project_id=project_id,
            respondent_id=respondent.id,
            criterion_a_id=pv["criterion_a_id"],
            criterion_b_id=pv["criterion_b_id"],
            value=pv["value"],
        )
        session.add(pw)

    # Save alternative scores (using expert-derived defaults from the Criteria)
    for c in criteria:
        for outcome, score_val in [
            ("vendor", c.vendor_score),
            ("hybrid", c.hybrid_score),
            ("independent", c.independent_score),
        ]:
            alt = AlternativeScore(
                id=generate_uuid(),
                project_id=project_id,
                respondent_id=respondent.id,
                criterion_id=c.id,
                outcome=outcome,
                score=score_val,
            )
            session.add(alt)

    await session.commit()

    return {
        "status": "valid",
        "respondent_id": respondent.id,
        "respondent_name": respondent.name,
        "respondent_role": respondent.role,
        "pairwise_count": len(survey_data.get("pairwise_values", [])),
        "alternative_score_count": len(survey_data.get("alternative_scores", [])),
        "warnings": validation["warnings"],
    }


@router.get("/projects/{project_id}/surveys")
async def list_surveys(project_id: str, session: AsyncSession = Depends(get_session)):
    """List uploaded survey files / respondents."""
    result = await session.execute(
        select(Respondent).where(Respondent.project_id == project_id).order_by(Respondent.created_at)
    )
    respondents = result.scalars().all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "role": r.role,
            "file": r.imported_from_file,
            "status": r.upload_status,
            "consistency_ratio": r.consistency_ratio,
            "created_at": r.created_at.isoformat(),
        }
        for r in respondents
    ]
