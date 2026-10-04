"""
Chat endpoints for Athena AI/CS Study Assistant.
Provides REST and Server-Sent Events (SSE) streaming for real-time pedagogical responses.
"""
import json
import asyncio
import logging
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import (
    ChatRequest, ChatResponse, StreamChunk, WebSource,
    CodeAnalysisResult, ApprovalDecisionRequest
)
from app.agents.orchestrator import run_orchestrator
from app.memory.session_memory import session_memory
from app.middleware.security import approval_manager, sanitize_user_input
from app.memory.learner_profile import profile_store
from app.database.db import get_db_session, save_message

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
async def post_chat(req: ChatRequest, db: AsyncSession = Depends(get_db_session)):
    """
    Standard JSON endpoint for multi-agent chat interactions.
    """
    clean_msg = sanitize_user_input(req.message)
    user_id = req.user_id or "guest"
    session_id = req.session_id

    # Record user message in DB
    try:
        await save_message(db, session_id, "user", clean_msg, user_id=user_id)
    except Exception as e:
        logger.warning(f"Failed to persist message to database: {e}")

    # Run LangGraph Orchestrator
    try:
        final_state = await run_orchestrator(
            user_id=user_id,
            session_id=session_id,
            message=clean_msg,
            learning_level=req.learning_level.value,
            explanation_depth=req.explanation_depth.value,
            learning_goal=req.learning_goal,
            require_search=bool(req.require_search)
        )
    except Exception as e:
        logger.error(f"Orchestrator error: {e}")
        raise HTTPException(status_code=500, detail=f"Orchestration failure: {str(e)}")

    response_text = final_state.get("final_response", "Explanation completed.")
    active_agent = final_state.get("active_agent", "Tutor Agent")
    agents_involved = final_state.get("requested_agents", ["Orchestrator Agent", active_agent])
    
    # Track topic in learner profile
    topic = final_state.get("current_topic", "Computer Science")
    profile_store.record_study_topic(user_id, topic)

    # Persist assistant message
    try:
        await save_message(db, session_id, "assistant", response_text, user_id=user_id, metadata={"agent": active_agent})
    except Exception as e:
        logger.warning(f"Failed to persist assistant reply: {e}")

    # Build sources & code analysis
    sources = [WebSource(**s) for s in final_state.get("web_sources", [])]
    code_out = final_state.get("coding_output")
    code_analysis = CodeAnalysisResult(**code_out) if code_out else None

    return ChatResponse(
        session_id=session_id,
        response=response_text,
        active_agent=active_agent,
        agents_involved=list(set(agents_involved)),
        sources=sources,
        code_analysis=code_analysis,
        approval_required=False
    )

@router.post("/stream")
async def post_chat_stream(req: ChatRequest):
    """
    Server-Sent Events (SSE) streaming endpoint.
    Emits real-time agent activity indicators, response tokens, and sources.
    """
    clean_msg = sanitize_user_input(req.message)
    user_id = req.user_id or "guest"
    session_id = req.session_id

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # 1. Orchestrator analyzing
            yield f"data: {json.dumps({'type': 'status', 'agent': 'Orchestrator Agent', 'content': 'Analyzing query & active context...'})}\n\n"
            await asyncio.sleep(0.08)

            # Heuristic status indicators
            req_l = clean_msg.lower()
            if any(k in req_l for k in ["research", "search", "arxiv", "latest"]):
                yield f"data: {json.dumps({'type': 'status', 'agent': 'Research Agent', 'content': 'Searching academic and official technical sources...'})}\n\n"
                await asyncio.sleep(0.08)
            elif any(k in req_l for k in ["code", "debug", "python", "complexity"]):
                yield f"data: {json.dumps({'type': 'status', 'agent': 'Coding Agent', 'content': 'Performing safe static AST code analysis...'})}\n\n"
                await asyncio.sleep(0.08)
            elif any(k in req_l for k in ["quiz", "test", "assessment", "exam"]):
                yield f"data: {json.dumps({'type': 'status', 'agent': 'Assessment Agent', 'content': 'Formulating diagnostic evaluation questions...'})}\n\n"
                await asyncio.sleep(0.08)
            else:
                yield f"data: {json.dumps({'type': 'status', 'agent': 'Tutor Agent', 'content': f'Structuring {req.explanation_depth.value} explanation for {req.learning_level.value} level...'})}\n\n"
                await asyncio.sleep(0.08)

            # Run orchestrator
            final_state = await run_orchestrator(
                user_id=user_id,
                session_id=session_id,
                message=clean_msg,
                learning_level=req.learning_level.value,
                explanation_depth=req.explanation_depth.value,
                learning_goal=req.learning_goal,
                require_search=bool(req.require_search)
            )

            response_text = final_state.get("final_response", "")
            active_agent = final_state.get("active_agent", "Tutor Agent")

            # Stream chunks of text
            chunk_size = 28
            for i in range(0, len(response_text), chunk_size):
                sub_token = response_text[i:i+chunk_size]
                yield f"data: {json.dumps({'type': 'token', 'agent': active_agent, 'content': sub_token})}\n\n"
                await asyncio.sleep(0.02)

            # Emit sources if any
            sources = final_state.get("web_sources", [])
            if sources:
                yield f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n"

            # Final done event
            yield f"data: {json.dumps({'type': 'done', 'agent': active_agent, 'session_id': session_id})}\n\n"

        except Exception as e:
            logger.error(f"SSE stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/approval")
async def handle_approval(decision: ApprovalDecisionRequest):
    """
    Submits user approval/rejection for an action paused at a checkpoint.
    """
    resolved = approval_manager.resolve_approval(decision.approval_token, decision.approved)
    if not resolved:
        return {"success": False, "message": "Approval token expired or invalid."}
    
    return {
        "success": True,
        "message": f"Action '{resolved.action_type}' has been {'approved and executed' if decision.approved else 'rejected'}."
    }
