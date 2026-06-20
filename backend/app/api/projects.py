"""
AlphaAlign — Project CRUD endpoints.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.db.models import Project, generate_uuid

router = APIRouter()


# ── Pydantic Schemas ──

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    company_name: str = Field(..., min_length=1, max_length=255)
    industry: str = ""
    owner: str = ""
    time_horizon: str = ""
    description: str = ""
    primary_vendor: str = ""
    key_systems: str = "[]"
    ai_ambition: str = ""
    notes: str = ""
    strategic_goals: str = ""
    regulatory_constraints: str = ""
    incumbent_vendors: str = ""
    internal_capabilities: str = ""


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None
    owner: Optional[str] = None
    time_horizon: Optional[str] = None
    description: Optional[str] = None
    primary_vendor: Optional[str] = None
    key_systems: Optional[str] = None
    ai_ambition: Optional[str] = None
    notes: Optional[str] = None
    strategic_goals: Optional[str] = None
    regulatory_constraints: Optional[str] = None
    incumbent_vendors: Optional[str] = None
    internal_capabilities: Optional[str] = None
    status: Optional[str] = None
    scoring_mode: Optional[str] = None
    aggregation_method: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    company_name: str
    industry: str
    owner: str
    time_horizon: str
    description: str
    primary_vendor: str
    key_systems: str
    ai_ambition: str
    notes: str
    strategic_goals: str
    regulatory_constraints: str
    incumbent_vendors: str
    internal_capabilities: str
    status: str
    scoring_mode: str
    aggregation_method: str
    created_at: datetime
    updated_at: datetime
    criteria_count: int = 0
    respondent_count: int = 0

    class Config:
        from_attributes = True


# ── Endpoints ──

@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(data: ProjectCreate, session: AsyncSession = Depends(get_session)):
    from app.api.criteria import DEFAULT_CRITERIA
    from app.db.models import Criterion
    
    project = Project(
        id=generate_uuid(),
        **data.model_dump(),
    )
    session.add(project)
    
    # Automatically inject the 10 fixed criteria
    for i, default in enumerate(DEFAULT_CRITERIA):
        criterion = Criterion(
            id=generate_uuid(),
            project_id=project.id,
            name=default["name"],
            description=default["description"],
            category=default["category"],
            sort_order=i,
            is_mandatory=True,
            vendor_score=default.get("vendor_score", 3.0),
            hybrid_score=default.get("hybrid_score", 3.0),
            independent_score=default.get("independent_score", 3.0),
        )
        session.add(criterion)
        
    await session.commit()
    
    # Reload with relationships to avoid lazy-loading in async context
    result = await session.execute(
        select(Project).options(
            selectinload(Project.criteria),
            selectinload(Project.respondents),
        ).where(Project.id == project.id)
    )
    project = result.scalar_one()
    return _to_response(project)


@router.get("/projects", response_model=list[ProjectResponse])
async def list_projects(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Project).options(
            selectinload(Project.criteria),
            selectinload(Project.respondents),
        ).order_by(Project.updated_at.desc())
    )
    projects = result.scalars().all()
    return [_to_response(p) for p in projects]


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, session: AsyncSession = Depends(get_session)):
    project = await _get_project(project_id, session)
    return _to_response(project)


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, data: ProjectUpdate, session: AsyncSession = Depends(get_session)):
    project = await _get_project(project_id, session)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    project.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(project)
    return _to_response(project)


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: str, session: AsyncSession = Depends(get_session)):
    project = await _get_project(project_id, session)
    await session.delete(project)
    await session.commit()


@router.post("/projects/{project_id}/duplicate", response_model=ProjectResponse, status_code=201)
async def duplicate_project(project_id: str, session: AsyncSession = Depends(get_session)):
    original = await _get_project(project_id, session)
    new_project = Project(
        id=generate_uuid(),
        name=f"{original.name} (Copy)",
        company_name=original.company_name,
        industry=original.industry,
        owner=original.owner,
        time_horizon=original.time_horizon,
        description=original.description,
        primary_vendor=original.primary_vendor,
        key_systems=original.key_systems,
        ai_ambition=original.ai_ambition,
        notes=original.notes,
        strategic_goals=original.strategic_goals,
        regulatory_constraints=original.regulatory_constraints,
        incumbent_vendors=original.incumbent_vendors,
        internal_capabilities=original.internal_capabilities,
        scoring_mode=original.scoring_mode,
        aggregation_method=original.aggregation_method,
    )
    session.add(new_project)
    await session.commit()
    await session.refresh(new_project)
    return _to_response(new_project)


# ── Helpers ──

async def _get_project(project_id: str, session: AsyncSession) -> Project:
    result = await session.execute(
        select(Project).options(
            selectinload(Project.criteria),
            selectinload(Project.respondents),
        ).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _to_response(project: Project) -> ProjectResponse:
    # Use getattr to safely access relationships that may not be loaded
    # Check __dict__ to avoid triggering lazy-loading in async context
    state = project.__dict__
    criteria = state.get('criteria', None)
    respondents = state.get('respondents', None)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        company_name=project.company_name,
        industry=project.industry,
        owner=project.owner,
        time_horizon=project.time_horizon,
        description=project.description,
        primary_vendor=project.primary_vendor,
        key_systems=project.key_systems,
        ai_ambition=project.ai_ambition,
        notes=project.notes,
        strategic_goals=project.strategic_goals,
        regulatory_constraints=project.regulatory_constraints,
        incumbent_vendors=project.incumbent_vendors,
        internal_capabilities=project.internal_capabilities,
        status=project.status,
        scoring_mode=project.scoring_mode,
        aggregation_method=project.aggregation_method,
        created_at=project.created_at,
        updated_at=project.updated_at,
        criteria_count=len(criteria) if criteria is not None else 0,
        respondent_count=len(respondents) if respondents is not None else 0,
    )
