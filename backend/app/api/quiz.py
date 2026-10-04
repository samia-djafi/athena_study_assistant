"""
Quiz and assessment API endpoints for Athena.
Provides quiz generation, answer submission, scoring, and knowledge gap detection.
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import (
    QuizGenerateRequest, QuizGenerateResponse,
    QuizSubmissionRequest, QuizSubmissionResponse
)
from app.agents.assessment_agent import generate_quiz, evaluate_quiz_submission, generate_default_questions_for_topic
from app.memory.learner_profile import profile_store
from app.database.db import get_db_session, DBQuizAttempt

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/quiz", tags=["Quiz & Assessment"])

# Cache of generated questions by quiz_id
QUIZ_STORE: Dict[str, Any] = {}

@router.post("/generate", response_model=QuizGenerateResponse)
async def api_generate_quiz(req: QuizGenerateRequest):
    """
    Generates structured assessment questions for a given CS/AI topic.
    """
    quiz_res = await generate_quiz(req.topic, req.learning_level, req.count)
    # Store in memory for verification upon submission
    QUIZ_STORE[quiz_res.quiz_id] = quiz_res
    return quiz_res

@router.post("/submit", response_model=QuizSubmissionResponse)
async def api_submit_quiz(submission: QuizSubmissionRequest, db: AsyncSession = Depends(get_db_session)):
    """
    Evaluates submitted answers, explains mistakes, and records learning progress.
    """
    cached_quiz = QUIZ_STORE.get(submission.quiz_id)
    if cached_quiz:
        original_questions = cached_quiz.questions
    else:
        # Re-derive questions if cache evicted
        original_questions = generate_default_questions_for_topic(submission.topic, "intermediate", len(submission.answers))

    eval_result = evaluate_quiz_submission(submission, original_questions)

    # Record in persistent learner profile
    profile_store.record_quiz_result(
        user_id=submission.user_id,
        percentage=eval_result.percentage,
        knowledge_gaps=eval_result.knowledge_gaps
    )

    # Record attempt in database
    try:
        attempt = DBQuizAttempt(
            user_id=submission.user_id,
            topic=submission.topic,
            score=eval_result.score,
            total=eval_result.total,
            percentage=eval_result.percentage,
            evaluations_json=[e.model_dump() for e in eval_result.evaluations],
            knowledge_gaps_json=eval_result.knowledge_gaps,
            recommended_revision_json=eval_result.recommended_revision
        )
        db.add(attempt)
        await db.commit()
    except Exception as e:
        logger.warning(f"Could not persist quiz attempt: {e}")

    return eval_result
