"""
AlphaAlign — LLM Analysis API endpoints.
"""

import json
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.db.models import LLMSettings, AHPResult, LLMAnalysisResult, generate_uuid
from app.llm.client import call_llm, test_connection
from app.llm.prompts import SYSTEM_PROMPT, ANALYSIS_PROMPTS

router = APIRouter()


class LLMSettingsInput(BaseModel):
    provider: str = ""
    model: str = ""
    endpoint: str = ""
    api_key: str = ""
    temperature: float = 0.7
    max_tokens: int = 2000
    use_local: bool = False
    anonymize_input: bool = False
    enabled: bool = False


class AnalysisRequest(BaseModel):
    analysis_type: str = "executive_summary"  # executive_summary, risk_analysis, alignment_interpretation, roadmap


@router.get("/projects/{project_id}/llm-settings")
async def get_llm_settings(project_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(LLMSettings).where(LLMSettings.project_id == project_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        return {"enabled": False}
    return {
        "id": settings.id,
        "provider": settings.provider,
        "model": settings.model,
        "endpoint": settings.endpoint,
        "api_key": "***" if settings.api_key else "",
        "temperature": settings.temperature,
        "max_tokens": settings.max_tokens,
        "use_local": settings.use_local,
        "anonymize_input": settings.anonymize_input,
        "enabled": settings.enabled,
    }


@router.post("/projects/{project_id}/llm-settings")
async def save_llm_settings(
    project_id: str, data: LLMSettingsInput,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(LLMSettings).where(LLMSettings.project_id == project_id)
    )
    settings = result.scalar_one_or_none()

    if settings:
        for key, value in data.model_dump().items():
            if key == "api_key" and value == "***":
                continue  # Don't overwrite with masked value
            setattr(settings, key, value)
    else:
        settings = LLMSettings(
            id=generate_uuid(),
            project_id=project_id,
            **data.model_dump(),
        )
        session.add(settings)

    await session.commit()
    return {"status": "ok"}


@router.post("/projects/{project_id}/test-llm-connection")
async def test_llm(project_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(LLMSettings).where(LLMSettings.project_id == project_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        raise HTTPException(400, "LLM settings not configured")

    conn_result = await test_connection(
        provider=settings.provider,
        endpoint=settings.endpoint,
        api_key=settings.api_key,
        model=settings.model,
    )
    return conn_result


@router.post("/projects/{project_id}/generate-llm-analysis")
async def generate_analysis(
    project_id: str, data: AnalysisRequest,
    session: AsyncSession = Depends(get_session),
):
    # Get LLM settings
    result = await session.execute(
        select(LLMSettings).where(LLMSettings.project_id == project_id)
    )
    settings = result.scalar_one_or_none()
    if not settings or not settings.enabled:
        raise HTTPException(400, "LLM is not enabled for this project")

    # Get AHP results
    result = await session.execute(
        select(AHPResult).where(AHPResult.project_id == project_id).order_by(AHPResult.calculated_at.desc())
    )
    ahp = result.scalar_one_or_none()
    if not ahp:
        raise HTTPException(400, "No AHP results available. Run the calculation first.")

    # Build analysis data
    analysis_data = {
        "criteria_weights": json.loads(ahp.criteria_weights),
        "outcome_scores": json.loads(ahp.outcome_scores),
        "final_scores": json.loads(ahp.final_scores),
        "alignment": json.loads(ahp.alignment_data),
        "recommendation": json.loads(ahp.recommendation),
    }

    # Get prompt builder
    prompt_builder = ANALYSIS_PROMPTS.get(data.analysis_type)
    if not prompt_builder:
        raise HTTPException(400, f"Unknown analysis type: {data.analysis_type}")

    prompt = prompt_builder(analysis_data)

    # Call LLM
    llm_result = await call_llm(
        provider=settings.provider,
        model=settings.model,
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        endpoint=settings.endpoint,
        api_key=settings.api_key,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
    )

    if llm_result.get("error"):
        raise HTTPException(500, f"LLM error: {llm_result['error']}")

    # Save result
    analysis_record = LLMAnalysisResult(
        id=generate_uuid(),
        project_id=project_id,
        analysis_type=data.analysis_type,
        prompt_used=prompt,
        response_text=llm_result["text"],
        provider_used=settings.provider,
        model_used=settings.model,
    )
    session.add(analysis_record)
    await session.commit()

    return {
        "analysis_type": data.analysis_type,
        "text": llm_result["text"],
        "provider": settings.provider,
        "model": settings.model,
        "tokens_used": llm_result.get("tokens_used", 0),
    }


@router.get("/projects/{project_id}/llm-analysis")
async def get_analysis(project_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(LLMAnalysisResult)
        .where(LLMAnalysisResult.project_id == project_id)
        .order_by(LLMAnalysisResult.created_at.desc())
    )
    analyses = result.scalars().all()
    return [
        {
            "id": a.id,
            "analysis_type": a.analysis_type,
            "text": a.response_text,
            "provider": a.provider_used,
            "model": a.model_used,
            "created_at": a.created_at.isoformat(),
        }
        for a in analyses
    ]
