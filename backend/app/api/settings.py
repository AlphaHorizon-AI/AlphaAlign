"""
AlphaAlign — Global Settings API.
Single-row settings for company profile and default AI model configuration.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_session
from app.db.models import GlobalSettings

router = APIRouter()


class SettingsResponse(BaseModel):
    # Company Profile
    company_name: str = ""
    industry: str = ""
    company_size: str = ""
    headquarters: str = ""
    website: str = ""
    primary_contact: str = ""
    primary_contact_email: str = ""
    primary_vendor_ecosystem: str = ""
    key_systems: str = ""
    ai_maturity_level: str = ""
    notes: str = ""
    # AI Model
    llm_provider: str = ""
    llm_model: str = ""
    llm_endpoint: str = ""
    llm_api_key: str = ""
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    llm_anonymize: bool = False
    llm_enabled: bool = False


class SettingsUpdate(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    headquarters: Optional[str] = None
    website: Optional[str] = None
    primary_contact: Optional[str] = None
    primary_contact_email: Optional[str] = None
    primary_vendor_ecosystem: Optional[str] = None
    key_systems: Optional[str] = None
    ai_maturity_level: Optional[str] = None
    notes: Optional[str] = None
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_endpoint: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_temperature: Optional[float] = None
    llm_max_tokens: Optional[int] = None
    llm_anonymize: Optional[bool] = None
    llm_enabled: Optional[bool] = None


async def _get_or_create(session: AsyncSession) -> GlobalSettings:
    """Get the single settings row, or create it if it doesn't exist."""
    result = await session.execute(select(GlobalSettings).limit(1))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = GlobalSettings()
        session.add(settings)
        await session.commit()
        await session.refresh(settings)
    return settings


@router.get("/settings", response_model=SettingsResponse)
async def get_settings(session: AsyncSession = Depends(get_session)):
    settings = await _get_or_create(session)
    return SettingsResponse(
        company_name=settings.company_name,
        industry=settings.industry,
        company_size=settings.company_size,
        headquarters=settings.headquarters,
        website=settings.website,
        primary_contact=settings.primary_contact,
        primary_contact_email=settings.primary_contact_email,
        primary_vendor_ecosystem=settings.primary_vendor_ecosystem,
        key_systems=settings.key_systems,
        ai_maturity_level=settings.ai_maturity_level,
        notes=settings.notes,
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
        llm_endpoint=settings.llm_endpoint,
        llm_api_key=settings.llm_api_key,
        llm_temperature=settings.llm_temperature,
        llm_max_tokens=settings.llm_max_tokens,
        llm_anonymize=settings.llm_anonymize,
        llm_enabled=settings.llm_enabled,
    )


@router.put("/settings", response_model=SettingsResponse)
async def update_settings(body: SettingsUpdate, session: AsyncSession = Depends(get_session)):
    settings = await _get_or_create(session)
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)
    await session.commit()
    await session.refresh(settings)
    return SettingsResponse(
        company_name=settings.company_name,
        industry=settings.industry,
        company_size=settings.company_size,
        headquarters=settings.headquarters,
        website=settings.website,
        primary_contact=settings.primary_contact,
        primary_contact_email=settings.primary_contact_email,
        primary_vendor_ecosystem=settings.primary_vendor_ecosystem,
        key_systems=settings.key_systems,
        ai_maturity_level=settings.ai_maturity_level,
        notes=settings.notes,
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
        llm_endpoint=settings.llm_endpoint,
        llm_api_key=settings.llm_api_key,
        llm_temperature=settings.llm_temperature,
        llm_max_tokens=settings.llm_max_tokens,
        llm_anonymize=settings.llm_anonymize,
        llm_enabled=settings.llm_enabled,
    )
