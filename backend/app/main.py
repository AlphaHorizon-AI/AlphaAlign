"""
AlphaAlign — FastAPI main application.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    await init_db()
    # Ensure upload and export directories exist
    (Path(__file__).parent.parent / "data" / "uploads").mkdir(parents=True, exist_ok=True)
    (Path(__file__).parent.parent / "data" / "exports").mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="AlphaAlign — Strategic AI Choice Engine",
    description="Decision-support API for AI architecture positioning, AHP scoring, and strategic recommendation.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow local React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register API routers ──
from app.api.projects import router as projects_router
from app.api.criteria import router as criteria_router
from app.api.respondents import router as respondents_router
from app.api.surveys import router as surveys_router
from app.api.calculation import router as calculation_router
from app.api.strategic import router as strategic_router
from app.api.llm import router as llm_router
from app.api.reports import router as reports_router
from app.api.settings import router as settings_router

app.include_router(projects_router, prefix="/api", tags=["Projects"])
app.include_router(criteria_router, prefix="/api", tags=["Criteria"])
app.include_router(respondents_router, prefix="/api", tags=["Respondents"])
app.include_router(surveys_router, prefix="/api", tags=["Surveys"])
app.include_router(calculation_router, prefix="/api", tags=["Calculation"])
app.include_router(strategic_router, prefix="/api", tags=["Strategic Importance"])
app.include_router(llm_router, prefix="/api", tags=["LLM Analysis"])
app.include_router(reports_router, prefix="/api", tags=["Reports"])
app.include_router(settings_router, prefix="/api", tags=["Settings"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "application": "AlphaAlign", "version": "1.0.0"}
