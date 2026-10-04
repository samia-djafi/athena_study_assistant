"""
Session management endpoints for Athena.
Provides endpoints for retrieving, listing, and clearing learning sessions.
"""
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.db import get_db_session, DBSession, DBMessage, get_session_history
from app.memory.session_memory import session_memory
from app.models.schemas import ChatMessage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.get("")
async def list_sessions(user_id: str = "guest", db: AsyncSession = Depends(get_db_session)) -> List[Dict[str, Any]]:
    """Lists all saved sessions for the given user."""
    result = await db.execute(
        select(DBSession).where(DBSession.user_id == user_id).order_by(DBSession.updated_at.desc())
    )
    sessions = result.scalars().all()
    
    # If no sessions in DB, return standard default session
    if not sessions:
        return [{
            "id": "welcome-session",
            "title": "Introduction to AI & Data Structures",
            "topic": "Algorithms",
            "created_at": 1700000000.0,
            "updated_at": 1700000000.0,
            "message_count": 0
        }]
        
    return [
        {
            "id": s.id,
            "title": s.title,
            "topic": s.topic,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
            "summary": s.summary
        }
        for s in sessions
    ]

@router.get("/{session_id}")
async def get_session(session_id: str, user_id: str = "guest", db: AsyncSession = Depends(get_db_session)) -> Dict[str, Any]:
    """Retrieves session details and chronological message history."""
    result = await db.execute(select(DBSession).where(DBSession.id == session_id))
    db_session = result.scalar_one_or_none()
    
    if not db_session:
        # Check memory store fallback
        mem_msgs = session_memory.get_session_messages(session_id, user_id=user_id)
        return {
            "id": session_id,
            "title": "Active Learning Session",
            "topic": session_memory.get_topic(session_id),
            "messages": [m.model_dump() for m in mem_msgs]
        }

    if db_session.user_id != user_id and user_id != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized access to this session.")

    messages = await get_session_history(db, session_id)
    return {
        "id": db_session.id,
        "title": db_session.title,
        "topic": db_session.topic,
        "summary": db_session.summary,
        "created_at": db_session.created_at,
        "updated_at": db_session.updated_at,
        "messages": [m.model_dump() for m in messages]
    }

@router.delete("/{session_id}")
async def delete_session(session_id: str, user_id: str = "guest", db: AsyncSession = Depends(get_db_session)):
    """Deletes or clears a session while enforcing user ownership."""
    # Clear from in-memory cache
    try:
        session_memory.clear_session(session_id, user_id=user_id)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Unauthorized: You do not own this session.")

    # Delete from database
    result = await db.execute(select(DBSession).where(DBSession.id == session_id))
    db_session = result.scalar_one_or_none()
    if db_session:
        if db_session.user_id != user_id and user_id != "admin":
            raise HTTPException(status_code=403, detail="Unauthorized access to delete session.")
        await db.delete(db_session)
        await db.commit()

    return {"success": True, "message": f"Session {session_id} successfully cleared."}
