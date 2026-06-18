"""
AlphaAlign — AHP Calculation and Full Scoring Pipeline endpoints.
"""

import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.db.models import (
    Project, Criterion, Respondent, PairwiseResponse,
    AlternativeScore, StrategicImportance, AHPResult, generate_uuid
)
from app.core.ahp import calculate_ahp
from app.core.aggregation import aggregate_weights
from app.core.scoring import calculate_weighted_scores, aggregate_alternative_scores, rank_outcomes, OUTCOMES
from app.core.strategic_importance import calculate_final_score
from app.core.alignment import calculate_alignment
from app.core.recommendation import generate_recommendation

router = APIRouter()


@router.post("/projects/{project_id}/calculate-ahp")
async def run_ahp_calculation(project_id: str, session: AsyncSession = Depends(get_session)):
    """Run the full AHP calculation pipeline."""

    # 1. Get project with aggregation method
    result = await session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")

    # 2. Get active criteria
    result = await session.execute(
        select(Criterion)
        .where(Criterion.project_id == project_id, Criterion.active == True)
        .order_by(Criterion.sort_order)
    )
    criteria = result.scalars().all()
    criteria_ids = [c.id for c in criteria]
    criterion_names = {c.id: c.name for c in criteria}

    if len(criteria) < 2:
        raise HTTPException(400, "At least 2 criteria are required for AHP calculation.")

    # 3. Get respondents
    result = await session.execute(
        select(Respondent).where(Respondent.project_id == project_id)
    )
    respondents = result.scalars().all()
    if not respondents:
        raise HTTPException(400, "No respondents found. Upload survey files first.")

    # 4. Calculate AHP per respondent
    respondent_weights = {}
    respondent_consistency = {}
    respondent_details = {}

    for resp in respondents:
        result = await session.execute(
            select(PairwiseResponse).where(
                PairwiseResponse.project_id == project_id,
                PairwiseResponse.respondent_id == resp.id,
            )
        )
        pairwise = result.scalars().all()
        pv_list = [
            {"criterion_a_id": p.criterion_a_id, "criterion_b_id": p.criterion_b_id, "value": p.value}
            for p in pairwise
        ]

        ahp_result = calculate_ahp(criteria_ids, pv_list)
        respondent_weights[resp.id] = ahp_result["weights"]
        respondent_consistency[resp.id] = ahp_result["cr"]
        respondent_details[resp.id] = {
            "name": resp.name,
            "role": resp.role,
            **ahp_result,
        }

        # Update respondent consistency ratio
        resp.consistency_ratio = ahp_result["cr"]

    # 5. Aggregate weights
    respondent_weightings = None
    if project.aggregation_method == "role_based":
        from app.api.respondents import DEFAULT_ROLE_WEIGHTS
        respondent_weightings = {r.id: DEFAULT_ROLE_WEIGHTS.get(r.role, 1.0) for r in respondents}
    elif project.aggregation_method == "custom":
        respondent_weightings = {r.id: r.weighting for r in respondents}

    group_weights = aggregate_weights(respondent_weights, respondent_weightings)

    # 6. Get alternative scores and calculate outcome scores
    alt_score_data = {}
    for resp in respondents:
        result = await session.execute(
            select(AlternativeScore).where(
                AlternativeScore.project_id == project_id,
                AlternativeScore.respondent_id == resp.id,
            )
        )
        scores = result.scalars().all()
        alt_score_data[resp.id] = [
            {"criterion_id": s.criterion_id, "outcome": s.outcome, "score": s.score}
            for s in scores
        ]

    aggregated_alt_scores = aggregate_alternative_scores(alt_score_data, respondent_weightings)
    outcome_scores = calculate_weighted_scores(group_weights, aggregated_alt_scores)

    # 7. Apply strategic importance
    result = await session.execute(
        select(StrategicImportance).where(StrategicImportance.project_id == project_id)
    )
    strategic_items = result.scalars().all()

    final_scores = dict(outcome_scores)  # Start with base scores
    strategic_adjustments = []

    for si in strategic_items:
        if si.outcome in OUTCOMES:
            base = outcome_scores.get(si.outcome, 0)
            si_result = calculate_final_score(base, si.strategic_importance)
            final_scores[si.outcome] = si_result["final_score"]
            si.base_score = base
            si.final_score = si_result["final_score"]
            strategic_adjustments.append({
                "item_name": si.item_name,
                "outcome": si.outcome,
                **si_result,
            })

    # 8. Leadership alignment analysis
    respondent_roles = {r.id: r.role for r in respondents}
    alignment_data = calculate_alignment(respondent_weights, respondent_roles, criterion_names)

    # 9. Generate recommendation
    recommendation = generate_recommendation(
        outcome_scores=outcome_scores,
        final_scores=final_scores,
        criteria_weights=group_weights,
        alignment_data=alignment_data,
        criterion_names=criterion_names,
    )

    # 10. Save results
    # Delete old results
    result = await session.execute(
        select(AHPResult).where(AHPResult.project_id == project_id)
    )
    for old in result.scalars().all():
        await session.delete(old)

    ahp_result = AHPResult(
        id=generate_uuid(),
        project_id=project_id,
        criteria_weights=json.dumps(group_weights),
        respondent_weights=json.dumps({k: v for k, v in respondent_weights.items()}),
        respondent_consistency=json.dumps(respondent_consistency),
        outcome_scores=json.dumps(outcome_scores),
        final_scores=json.dumps(final_scores),
        alignment_data=json.dumps(alignment_data),
        recommendation=json.dumps(recommendation),
        aggregation_method=project.aggregation_method,
    )
    session.add(ahp_result)

    # Update project status
    project.status = "calculated"
    project.updated_at = datetime.utcnow()

    await session.commit()

    return {
        "criteria_weights": group_weights,
        "criterion_names": criterion_names,
        "respondent_details": respondent_details,
        "outcome_scores": outcome_scores,
        "final_scores": final_scores,
        "strategic_adjustments": strategic_adjustments,
        "alignment": alignment_data,
        "recommendation": recommendation,
        "aggregation_method": project.aggregation_method,
    }


@router.get("/projects/{project_id}/ahp-results")
async def get_ahp_results(project_id: str, session: AsyncSession = Depends(get_session)):
    """Retrieve cached AHP results."""
    result = await session.execute(
        select(AHPResult).where(AHPResult.project_id == project_id).order_by(AHPResult.calculated_at.desc())
    )
    ahp = result.scalar_one_or_none()
    if not ahp:
        raise HTTPException(404, "No AHP results found. Run the calculation first.")

    # Get criterion names
    result = await session.execute(
        select(Criterion).where(Criterion.project_id == project_id).order_by(Criterion.sort_order)
    )
    criteria = result.scalars().all()
    criterion_names = {c.id: c.name for c in criteria}

    return {
        "criteria_weights": json.loads(ahp.criteria_weights),
        "criterion_names": criterion_names,
        "respondent_weights": json.loads(ahp.respondent_weights),
        "respondent_consistency": json.loads(ahp.respondent_consistency),
        "outcome_scores": json.loads(ahp.outcome_scores),
        "final_scores": json.loads(ahp.final_scores),
        "alignment": json.loads(ahp.alignment_data),
        "recommendation": json.loads(ahp.recommendation),
        "aggregation_method": ahp.aggregation_method,
        "calculated_at": ahp.calculated_at.isoformat(),
    }
