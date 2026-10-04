"""
Learning progress and preferences API for Athena.
Provides learner analytics, preference customization, and user data controls.
"""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from app.models.schemas import LearnerProfile, LearningLevel, ExplanationDepth
from app.memory.learner_profile import profile_store

router = APIRouter(prefix="/learning", tags=["Learning & Analytics"])

class PreferenceUpdateRequest(BaseModel):
    user_id: str = "guest"
    preferred_level: Optional[LearningLevel] = None
    preferred_depth: Optional[ExplanationDepth] = None
    preferred_language: Optional[str] = None

@router.get("/progress", response_model=LearnerProfile)
async def get_progress(user_id: str = "guest"):
    """Returns learner profile metrics, study sessions, and review recommendations."""
    return profile_store.get_profile(user_id)

@router.post("/preferences", response_model=LearnerProfile)
async def update_preferences(req: PreferenceUpdateRequest):
    """Updates learner study preferences (level, depth, language)."""
    return profile_store.update_preferences(
        user_id=req.user_id,
        level=req.preferred_level,
        depth=req.preferred_depth,
        language=req.preferred_language
    )

@router.delete("/reset")
async def reset_learning_data(user_id: str = "guest"):
    """User privacy control: Resets all recorded learner history."""
    profile_store.delete_profile_data(user_id)
    return {"success": True, "message": "Learner study profile reset successfully."}
