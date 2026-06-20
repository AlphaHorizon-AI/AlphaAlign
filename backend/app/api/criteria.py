"""
AlphaAlign — Criteria CRUD endpoints with default criteria library.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.db.models import Criterion, generate_uuid

router = APIRouter()


# ── Default Criteria Library ──

DEFAULT_CRITERIA = [
    {
        "name": "Core Business Criticality",
        "description": "How critical are the planned AI use cases to the company's core value proposition and revenue generation?",
        "category": "Strategic",
        "vendor_score": 4.0, "hybrid_score": 4.0, "independent_score": 3.0,
    },
    {
        "name": "Autonomous Operations Ambition",
        "description": "To what extent do you envision AI taking autonomous actions (Agentic AI) versus just providing decision support?",
        "category": "Strategic",
        "vendor_score": 2.0, "hybrid_score": 3.0, "independent_score": 5.0,
    },
    {
        "name": "Enterprise Integration Complexity",
        "description": "How deeply must AI integrate with existing legacy systems, ERPs, CRMs, and proprietary data lakes?",
        "category": "Technical",
        "vendor_score": 4.0, "hybrid_score": 4.0, "independent_score": 2.0,
    },
    {
        "name": "Vendor Lock-in Tolerance",
        "description": "How acceptable is it to be highly dependent on a single major tech vendor for your AI capabilities?",
        "category": "Risk",
        "vendor_score": 1.0, "hybrid_score": 3.0, "independent_score": 5.0,
    },
    {
        "name": "Regulatory & Compliance Rigor",
        "description": "How strict are the regulatory, auditability, and data sovereignty requirements governing your industry?",
        "category": "Governance",
        "vendor_score": 3.0, "hybrid_score": 3.0, "independent_score": 4.0,
    },
    {
        "name": "Proprietary Data Sensitivity",
        "description": "How sensitive is the internal data and IP that will be processed by these AI systems?",
        "category": "Governance",
        "vendor_score": 2.0, "hybrid_score": 3.0, "independent_score": 5.0,
    },
    {
        "name": "Technological Agility Needs",
        "description": "How important is the ability to rapidly swap underlying AI models as technology evolves?",
        "category": "Technical",
        "vendor_score": 1.0, "hybrid_score": 4.0, "independent_score": 5.0,
    },
    {
        "name": "Cost Predictability Focus",
        "description": "How important is strict predictability and optimization of ongoing AI operational costs?",
        "category": "Financial",
        "vendor_score": 4.0, "hybrid_score": 3.0, "independent_score": 2.0,
    },
    {
        "name": "In-House AI Capability",
        "description": "How strong is your internal engineering, data science, and MLOps talent pool today?",
        "category": "Organizational",
        "vendor_score": 5.0, "hybrid_score": 3.0, "independent_score": 1.0,
    },
    {
        "name": "Time-to-Value Urgency",
        "description": "How urgently does the organization need to deploy functional AI capabilities to remain competitive?",
        "category": "Operational",
        "vendor_score": 5.0, "hybrid_score": 3.0, "independent_score": 2.0,
    },
]


# ── Pydantic Schemas ──

class CriterionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    category: str = ""
    is_mandatory: bool = False
    vendor_score: float = 3.0
    hybrid_score: float = 3.0
    independent_score: float = 3.0


class CriterionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    active: Optional[bool] = None
    is_mandatory: Optional[bool] = None
    sort_order: Optional[int] = None
    vendor_score: Optional[float] = None
    hybrid_score: Optional[float] = None
    independent_score: Optional[float] = None


class CriterionResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: str
    category: str
    active: bool
    sort_order: int
    is_mandatory: bool
    vendor_score: float
    hybrid_score: float
    independent_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class ReorderRequest(BaseModel):
    criterion_ids: List[str]


# ── Endpoints ──

@router.get("/projects/{project_id}/criteria", response_model=list[CriterionResponse])
async def list_criteria(project_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Criterion)
        .where(Criterion.project_id == project_id)
        .order_by(Criterion.sort_order, Criterion.created_at)
    )
    return result.scalars().all()


@router.post("/projects/{project_id}/criteria", response_model=CriterionResponse, status_code=201)
async def add_criterion(project_id: str, data: CriterionCreate, session: AsyncSession = Depends(get_session)):
    raise HTTPException(status_code=403, detail="Criteria are fixed for this assessment type and cannot be added.")

@router.post("/projects/{project_id}/criteria/defaults", response_model=list[CriterionResponse], status_code=201)
async def load_default_criteria(project_id: str, session: AsyncSession = Depends(get_session)):
    """Load the default criteria set for a project. Clears existing criteria first."""
    # Delete existing criteria
    result = await session.execute(
        select(Criterion).where(Criterion.project_id == project_id)
    )
    for c in result.scalars().all():
        await session.delete(c)

    # Create defaults
    criteria = []
    for i, default in enumerate(DEFAULT_CRITERIA):
        criterion = Criterion(
            id=generate_uuid(),
            project_id=project_id,
            name=default["name"],
            description=default["description"],
            category=default["category"],
            sort_order=i,
            is_mandatory=True, # All fixed criteria are mandatory
            vendor_score=default.get("vendor_score", 3.0),
            hybrid_score=default.get("hybrid_score", 3.0),
            independent_score=default.get("independent_score", 3.0),
        )
        session.add(criterion)
        criteria.append(criterion)

    await session.commit()
    for c in criteria:
        await session.refresh(c)
    return criteria


@router.patch("/projects/{project_id}/criteria/{criterion_id}", response_model=CriterionResponse)
async def update_criterion(
    project_id: str, criterion_id: str,
    data: CriterionUpdate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Criterion).where(Criterion.id == criterion_id, Criterion.project_id == project_id)
    )
    criterion = result.scalar_one_or_none()
    if not criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")

    # Only allow updating scores and description, not name
    update_data = data.model_dump(exclude_unset=True)
    if "name" in update_data:
        del update_data["name"]

    for key, value in update_data.items():
        setattr(criterion, key, value)

    await session.commit()
    await session.refresh(criterion)
    return criterion


@router.delete("/projects/{project_id}/criteria/{criterion_id}", status_code=204)
async def delete_criterion(project_id: str, criterion_id: str, session: AsyncSession = Depends(get_session)):
    raise HTTPException(status_code=403, detail="Criteria are fixed for this assessment type and cannot be deleted.")


@router.post("/projects/{project_id}/criteria/reorder", status_code=200)
async def reorder_criteria(project_id: str, data: ReorderRequest, session: AsyncSession = Depends(get_session)):
    for i, cid in enumerate(data.criterion_ids):
        result = await session.execute(
            select(Criterion).where(Criterion.id == cid, Criterion.project_id == project_id)
        )
        criterion = result.scalar_one_or_none()
        if criterion:
            criterion.sort_order = i

    await session.commit()
    return {"status": "ok"}
