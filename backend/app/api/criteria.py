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
        "name": "Business Criticality",
        "description": "How critical is AI to core business operations, revenue, and competitive advantage?",
        "category": "Strategic",
    },
    {
        "name": "Agentic Ambition",
        "description": "To what extent does the company plan to deploy autonomous AI agents across business processes?",
        "category": "Strategic",
    },
    {
        "name": "System Complexity",
        "description": "How many systems (ERP, CRM, data platforms, legacy) must AI interact with?",
        "category": "Technical",
    },
    {
        "name": "Vendor Dependency Risk",
        "description": "How concerned is the company about over-dependence on a single vendor ecosystem?",
        "category": "Risk",
    },
    {
        "name": "Governance and Compliance Need",
        "description": "How important are regulatory compliance, auditability, and AI governance controls?",
        "category": "Governance",
    },
    {
        "name": "Data and IP Sensitivity",
        "description": "How sensitive is the data and intellectual property involved in AI workflows?",
        "category": "Governance",
    },
    {
        "name": "Model Flexibility Requirement",
        "description": "How important is the ability to switch between AI models and providers?",
        "category": "Technical",
    },
    {
        "name": "Cost Control Pressure",
        "description": "How strongly does the company need to control and optimize AI-related costs?",
        "category": "Financial",
    },
    {
        "name": "Internal Capability Readiness",
        "description": "Does the company have the internal talent, skills, and maturity to operate independent AI?",
        "category": "Organizational",
    },
    {
        "name": "Speed to Implementation",
        "description": "How quickly must AI capabilities be deployed and operational?",
        "category": "Operational",
    },
]


# ── Pydantic Schemas ──

class CriterionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    category: str = ""
    is_mandatory: bool = False


class CriterionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    active: Optional[bool] = None
    is_mandatory: Optional[bool] = None
    sort_order: Optional[int] = None


class CriterionResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: str
    category: str
    active: bool
    sort_order: int
    is_mandatory: bool
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
    # Get max sort order
    result = await session.execute(
        select(Criterion.sort_order)
        .where(Criterion.project_id == project_id)
        .order_by(Criterion.sort_order.desc())
    )
    max_order = result.scalar() or 0

    criterion = Criterion(
        id=generate_uuid(),
        project_id=project_id,
        sort_order=max_order + 1,
        **data.model_dump(),
    )
    session.add(criterion)
    await session.commit()
    await session.refresh(criterion)
    return criterion


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
            is_mandatory=True if i < 5 else False,
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

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(criterion, key, value)

    await session.commit()
    await session.refresh(criterion)
    return criterion


@router.delete("/projects/{project_id}/criteria/{criterion_id}", status_code=204)
async def delete_criterion(project_id: str, criterion_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Criterion).where(Criterion.id == criterion_id, Criterion.project_id == project_id)
    )
    criterion = result.scalar_one_or_none()
    if not criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")

    await session.delete(criterion)
    await session.commit()


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
