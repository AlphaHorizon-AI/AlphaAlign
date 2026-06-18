"""
AlphaAlign — Respondent management endpoints.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.db.models import Respondent, generate_uuid

router = APIRouter()

# Default role weights from the build paper (Section 6)
DEFAULT_ROLE_WEIGHTS = {
    "CEO": 1.5,
    "CFO": 1.2,
    "CIO": 1.5,
    "CTO": 1.5,
    "CISO": 1.3,
    "COO": 1.2,
    "CHRO": 0.8,
    "Business Unit Leader": 1.0,
    "Data and AI Leader": 1.3,
    "Transformation Leader": 1.2,
    "Enterprise Architect": 1.0,
}


class RespondentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    role: str = ""
    email: str = ""
    weighting: float = 1.0


class RespondentUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    weighting: Optional[float] = None


class RespondentResponse(BaseModel):
    id: str
    project_id: str
    name: str
    role: str
    email: str
    weighting: float
    imported_from_file: str
    comments: str
    consistency_ratio: Optional[float]
    upload_status: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/projects/{project_id}/respondents", response_model=list[RespondentResponse])
async def list_respondents(project_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Respondent)
        .where(Respondent.project_id == project_id)
        .order_by(Respondent.created_at)
    )
    return result.scalars().all()


@router.post("/projects/{project_id}/respondents", response_model=RespondentResponse, status_code=201)
async def add_respondent(project_id: str, data: RespondentCreate, session: AsyncSession = Depends(get_session)):
    respondent = Respondent(
        id=generate_uuid(),
        project_id=project_id,
        **data.model_dump(),
    )
    session.add(respondent)
    await session.commit()
    await session.refresh(respondent)
    return respondent


@router.patch("/projects/{project_id}/respondents/{respondent_id}", response_model=RespondentResponse)
async def update_respondent(
    project_id: str, respondent_id: str,
    data: RespondentUpdate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Respondent).where(Respondent.id == respondent_id, Respondent.project_id == project_id)
    )
    respondent = result.scalar_one_or_none()
    if not respondent:
        raise HTTPException(status_code=404, detail="Respondent not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(respondent, key, value)
    await session.commit()
    await session.refresh(respondent)
    return respondent


@router.delete("/projects/{project_id}/respondents/{respondent_id}", status_code=204)
async def delete_respondent(project_id: str, respondent_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Respondent).where(Respondent.id == respondent_id, Respondent.project_id == project_id)
    )
    respondent = result.scalar_one_or_none()
    if not respondent:
        raise HTTPException(status_code=404, detail="Respondent not found")
    await session.delete(respondent)
    await session.commit()


@router.get("/default-role-weights")
async def get_default_role_weights():
    return DEFAULT_ROLE_WEIGHTS


@router.post("/projects/{project_id}/respondents/apply-role-weights", status_code=200)
async def apply_role_weights(project_id: str, session: AsyncSession = Depends(get_session)):
    """Apply default role-based weights to all respondents based on their role."""
    result = await session.execute(
        select(Respondent).where(Respondent.project_id == project_id)
    )
    respondents = result.scalars().all()
    for r in respondents:
        r.weighting = DEFAULT_ROLE_WEIGHTS.get(r.role, 1.0)
    await session.commit()
    return {"status": "ok", "updated": len(respondents)}
