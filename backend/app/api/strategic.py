"""
AlphaAlign — Strategic Importance CRUD endpoints.
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.db.models import StrategicImportance, generate_uuid
from app.core.strategic_importance import (
    calculate_final_score, validate_justification, get_strategic_importance_label
)

router = APIRouter()


class StrategicImportanceCreate(BaseModel):
    item_name: str = Field(..., min_length=1)
    item_type: str = "outcome"
    outcome: str = ""
    strategic_importance: int = Field(0, ge=0, le=10)
    justification: str = ""
    executive_sponsor: str = ""
    time_horizon: str = ""
    risk_of_not_acting: str = ""
    business_consequence: str = ""
    review_date: Optional[str] = None


class StrategicImportanceUpdate(BaseModel):
    item_name: Optional[str] = None
    strategic_importance: Optional[int] = None
    justification: Optional[str] = None
    executive_sponsor: Optional[str] = None
    time_horizon: Optional[str] = None
    risk_of_not_acting: Optional[str] = None
    business_consequence: Optional[str] = None
    review_date: Optional[str] = None
    include_in_report: Optional[bool] = None


@router.get("/projects/{project_id}/strategic-importance")
async def list_strategic_importance(project_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(StrategicImportance)
        .where(StrategicImportance.project_id == project_id)
        .order_by(StrategicImportance.created_at)
    )
    items = result.scalars().all()
    return [
        {
            "id": si.id,
            "item_name": si.item_name,
            "item_type": si.item_type,
            "outcome": si.outcome,
            "base_score": si.base_score,
            "strategic_importance": si.strategic_importance,
            "final_score": si.final_score,
            "justification": si.justification,
            "executive_sponsor": si.executive_sponsor,
            "time_horizon": si.time_horizon,
            "risk_of_not_acting": si.risk_of_not_acting,
            "business_consequence": si.business_consequence,
            "review_date": si.review_date.isoformat() if si.review_date else None,
            "include_in_report": si.include_in_report,
            "label": get_strategic_importance_label(si.strategic_importance),
            "score_calculation": calculate_final_score(si.base_score, si.strategic_importance),
        }
        for si in items
    ]


@router.post("/projects/{project_id}/strategic-importance", status_code=201)
async def add_strategic_importance(
    project_id: str, data: StrategicImportanceCreate,
    session: AsyncSession = Depends(get_session),
):
    # Validate justification if SI >= 7
    if data.strategic_importance >= 7:
        missing = validate_justification(data.strategic_importance, data.model_dump())
        if missing:
            raise HTTPException(400, f"Strategic Importance ≥ 7 requires: {', '.join(missing)}")

    review_date = None
    if data.review_date:
        try:
            review_date = date.fromisoformat(data.review_date)
        except ValueError:
            pass

    si = StrategicImportance(
        id=generate_uuid(),
        project_id=project_id,
        item_name=data.item_name,
        item_type=data.item_type,
        outcome=data.outcome,
        strategic_importance=data.strategic_importance,
        justification=data.justification,
        executive_sponsor=data.executive_sponsor,
        time_horizon=data.time_horizon,
        risk_of_not_acting=data.risk_of_not_acting,
        business_consequence=data.business_consequence,
        review_date=review_date,
    )
    session.add(si)
    await session.commit()
    await session.refresh(si)

    return {
        "id": si.id,
        "item_name": si.item_name,
        "strategic_importance": si.strategic_importance,
        "label": get_strategic_importance_label(si.strategic_importance),
    }


@router.patch("/projects/{project_id}/strategic-importance/{item_id}")
async def update_strategic_importance(
    project_id: str, item_id: str,
    data: StrategicImportanceUpdate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(StrategicImportance)
        .where(StrategicImportance.id == item_id, StrategicImportance.project_id == project_id)
    )
    si = result.scalar_one_or_none()
    if not si:
        raise HTTPException(404, "Strategic importance item not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        if key == "review_date" and value:
            try:
                setattr(si, key, date.fromisoformat(value))
            except ValueError:
                pass
        else:
            setattr(si, key, value)

    await session.commit()
    return {"status": "ok"}


@router.delete("/projects/{project_id}/strategic-importance/{item_id}", status_code=204)
async def delete_strategic_importance(
    project_id: str, item_id: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(StrategicImportance)
        .where(StrategicImportance.id == item_id, StrategicImportance.project_id == project_id)
    )
    si = result.scalar_one_or_none()
    if not si:
        raise HTTPException(404, "Strategic importance item not found")
    await session.delete(si)
    await session.commit()
