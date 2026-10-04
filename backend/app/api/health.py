"""
Health and diagnostic endpoint for Athena AI/CS Study Assistant.
"""
from fastapi import APIRouter
from app.config import settings
from app.models.schemas import HealthResponse
from app.tools.mcp_client import mcp_client

router = APIRouter(prefix="/health", tags=["System"])

@router.get("", response_model=HealthResponse)
async def health_check():
    """
    Returns platform health, active LLM provider, database status, and MCP status.
    """
    llm_prov = "Groq" if settings.GROQ_API_KEY else "Deterministic Educational Fallback"
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        llm_provider=llm_prov,
        database="SQLite (aiosqlite) / Supabase Ready",
        mcp_enabled=len(mcp_client.list_available_tools()) > 0
    )
