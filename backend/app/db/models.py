"""
AlphaAlign — SQLAlchemy ORM models.
Matches the data model from the build paper (Section 13).
"""

import uuid
from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import String, Text, Float, Boolean, Integer, DateTime, Date, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


# ──────────────────────────────────────────────
# Project
# ──────────────────────────────────────────────
class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str] = mapped_column(String(255), default="")
    owner: Mapped[str] = mapped_column(String(255), default="")
    time_horizon: Mapped[str] = mapped_column(String(100), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    primary_vendor: Mapped[str] = mapped_column(String(255), default="")
    key_systems: Mapped[str] = mapped_column(Text, default="")  # JSON array as string
    ai_ambition: Mapped[str] = mapped_column(String(100), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    
    # Strategic Context Fields (qualitative inputs for the LLM)
    strategic_goals: Mapped[str] = mapped_column(Text, default="")
    regulatory_constraints: Mapped[str] = mapped_column(Text, default="")
    incumbent_vendors: Mapped[str] = mapped_column(Text, default="")
    internal_capabilities: Mapped[str] = mapped_column(Text, default="")
    
    status: Mapped[str] = mapped_column(String(50), default="draft")
    scoring_mode: Mapped[str] = mapped_column(String(20), default="simple")
    aggregation_method: Mapped[str] = mapped_column(String(20), default="equal")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    criteria: Mapped[List["Criterion"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    respondents: Mapped[List["Respondent"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    strategic_items: Mapped[List["StrategicImportance"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    llm_settings: Mapped[Optional["LLMSettings"]] = relationship(back_populates="project", cascade="all, delete-orphan", uselist=False)


# ──────────────────────────────────────────────
# Criterion
# ──────────────────────────────────────────────
class Criterion(Base):
    __tablename__ = "criteria"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(100), default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Expert-derived outcome scores (1-5):  how well each AI architecture fits this criterion.
    # These are admin-tunable defaults so survey respondents don't have to score them.
    vendor_score: Mapped[float] = mapped_column(Float, default=3.0)      # Strong Vendor Commitment
    hybrid_score: Mapped[float] = mapped_column(Float, default=3.0)      # Hybrid AI Operating Model
    independent_score: Mapped[float] = mapped_column(Float, default=3.0) # Independent AI Control Model

    project: Mapped["Project"] = relationship(back_populates="criteria")


# ──────────────────────────────────────────────
# Respondent
# ──────────────────────────────────────────────
class Respondent(Base):
    __tablename__ = "respondents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(100), default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    weighting: Mapped[float] = mapped_column(Float, default=1.0)
    imported_from_file: Mapped[str] = mapped_column(String(255), default="")
    comments: Mapped[str] = mapped_column(Text, default="")
    consistency_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    upload_status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, valid, invalid
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="respondents")
    pairwise_responses: Mapped[List["PairwiseResponse"]] = relationship(back_populates="respondent", cascade="all, delete-orphan")
    alternative_scores: Mapped[List["AlternativeScore"]] = relationship(back_populates="respondent", cascade="all, delete-orphan")


# ──────────────────────────────────────────────
# PairwiseResponse (AHP comparison values)
# ──────────────────────────────────────────────
class PairwiseResponse(Base):
    __tablename__ = "pairwise_responses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    respondent_id: Mapped[str] = mapped_column(String(36), ForeignKey("respondents.id"), nullable=False)
    criterion_a_id: Mapped[str] = mapped_column(String(36), ForeignKey("criteria.id"), nullable=False)
    criterion_b_id: Mapped[str] = mapped_column(String(36), ForeignKey("criteria.id"), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)  # 1/9 to 9
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    respondent: Mapped["Respondent"] = relationship(back_populates="pairwise_responses")


# ──────────────────────────────────────────────
# AlternativeScore (outcome scoring per criterion)
# ──────────────────────────────────────────────
class AlternativeScore(Base):
    __tablename__ = "alternative_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    respondent_id: Mapped[str] = mapped_column(String(36), ForeignKey("respondents.id"), nullable=False)
    criterion_id: Mapped[str] = mapped_column(String(36), ForeignKey("criteria.id"), nullable=False)
    outcome: Mapped[str] = mapped_column(String(50), nullable=False)  # vendor, hybrid, independent
    score: Mapped[float] = mapped_column(Float, nullable=False)  # 1-5
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    respondent: Mapped["Respondent"] = relationship(back_populates="alternative_scores")


# ──────────────────────────────────────────────
# StrategicImportance
# ──────────────────────────────────────────────
class StrategicImportance(Base):
    __tablename__ = "strategic_importance"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), default="outcome")  # outcome, initiative, project
    outcome: Mapped[str] = mapped_column(String(50), default="")  # vendor, hybrid, independent
    base_score: Mapped[float] = mapped_column(Float, default=0.0)
    strategic_importance: Mapped[int] = mapped_column(Integer, default=0)
    final_score: Mapped[float] = mapped_column(Float, default=0.0)
    justification: Mapped[str] = mapped_column(Text, default="")
    executive_sponsor: Mapped[str] = mapped_column(String(255), default="")
    time_horizon: Mapped[str] = mapped_column(String(100), default="")
    risk_of_not_acting: Mapped[str] = mapped_column(Text, default="")
    business_consequence: Mapped[str] = mapped_column(Text, default="")
    review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    include_in_report: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="strategic_items")


# ──────────────────────────────────────────────
# LLMSettings (per-project LLM configuration)
# ──────────────────────────────────────────────
class LLMSettings(Base):
    __tablename__ = "llm_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False, unique=True)
    provider: Mapped[str] = mapped_column(String(50), default="")  # openai, anthropic, ollama, lmstudio, azure, custom
    model: Mapped[str] = mapped_column(String(100), default="")
    endpoint: Mapped[str] = mapped_column(String(500), default="")
    api_key: Mapped[str] = mapped_column(String(500), default="")
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, default=2000)
    use_local: Mapped[bool] = mapped_column(Boolean, default=False)
    anonymize_input: Mapped[bool] = mapped_column(Boolean, default=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="llm_settings")


# ──────────────────────────────────────────────
# AHP Results (cached calculation results)
# ──────────────────────────────────────────────
class AHPResult(Base):
    __tablename__ = "ahp_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    criteria_weights: Mapped[str] = mapped_column(Text, default="{}")  # JSON: {criterion_id: weight}
    respondent_weights: Mapped[str] = mapped_column(Text, default="{}")  # JSON: {resp_id: {criterion_id: weight}}
    respondent_consistency: Mapped[str] = mapped_column(Text, default="{}")  # JSON: {resp_id: CR}
    outcome_scores: Mapped[str] = mapped_column(Text, default="{}")  # JSON: {vendor: x, hybrid: y, independent: z}
    final_scores: Mapped[str] = mapped_column(Text, default="{}")  # JSON: with strategic adjustments
    alignment_data: Mapped[str] = mapped_column(Text, default="{}")  # JSON: alignment analysis
    recommendation: Mapped[str] = mapped_column(Text, default="{}")  # JSON: recommendation object
    aggregation_method: Mapped[str] = mapped_column(String(20), default="equal")
    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    
# ──────────────────────────────────────────────
# LLM Analysis Results (cached LLM output)
# ──────────────────────────────────────────────
class LLMAnalysisResult(Base):
    __tablename__ = "llm_analysis_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    analysis_type: Mapped[str] = mapped_column(String(50), default="executive_summary")
    prompt_used: Mapped[str] = mapped_column(Text, default="")
    response_text: Mapped[str] = mapped_column(Text, default="")
    provider_used: Mapped[str] = mapped_column(String(100), default="")
    model_used: Mapped[str] = mapped_column(String(100), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ──────────────────────────────────────────────
# GlobalSettings (app-wide settings, single row)
# ──────────────────────────────────────────────
class GlobalSettings(Base):
    __tablename__ = "global_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)

    # Company Profile
    company_name: Mapped[str] = mapped_column(String(255), default="")
    industry: Mapped[str] = mapped_column(String(255), default="")
    company_size: Mapped[str] = mapped_column(String(100), default="")
    headquarters: Mapped[str] = mapped_column(String(255), default="")
    website: Mapped[str] = mapped_column(String(500), default="")
    primary_contact: Mapped[str] = mapped_column(String(255), default="")
    primary_contact_email: Mapped[str] = mapped_column(String(255), default="")
    primary_vendor_ecosystem: Mapped[str] = mapped_column(String(255), default="")
    key_systems: Mapped[str] = mapped_column(Text, default="")
    ai_maturity_level: Mapped[str] = mapped_column(String(100), default="")
    notes: Mapped[str] = mapped_column(Text, default="")

    # Default AI Model Settings
    llm_provider: Mapped[str] = mapped_column(String(50), default="")
    llm_model: Mapped[str] = mapped_column(String(100), default="")
    llm_endpoint: Mapped[str] = mapped_column(String(500), default="")
    llm_api_key: Mapped[str] = mapped_column(String(500), default="")
    llm_temperature: Mapped[float] = mapped_column(Float, default=0.7)
    llm_max_tokens: Mapped[int] = mapped_column(Integer, default=2000)
    llm_anonymize: Mapped[bool] = mapped_column(Boolean, default=False)
    llm_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

