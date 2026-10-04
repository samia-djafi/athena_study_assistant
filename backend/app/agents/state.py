"""
Shared LangGraph state schema for Athena Multi-Agent Architecture.
Defines all 21 typed fields required by Section 4.
"""
from typing import TypedDict, List, Dict, Any, Optional
from app.models.schemas import (
    ChatMessage, WebSource, CodeAnalysisResult,
    QuizQuestion, QuizSubmissionResponse
)

class AthenaState(TypedDict, total=False):
    # Core identifiers & preferences
    user_id: str
    session_id: str
    current_request: str
    current_topic: str
    learning_level: str          # "beginner" | "intermediate" | "advanced"
    explanation_depth: str       # "short" | "standard" | "detailed"
    learning_goal: Optional[str]
    
    # Conversational memory & agents
    conversation_messages: List[Dict[str, Any]]
    relevant_memory: Dict[str, Any]
    requested_agents: List[str]
    active_agent: str
    
    # Domain data & specialist outputs
    retrieved_documents: List[Dict[str, Any]]
    web_sources: List[Dict[str, Any]]
    research_findings: Optional[str]
    tutor_output: Optional[str]
    coding_output: Optional[Dict[str, Any]]
    assessment_output: Optional[Dict[str, Any]]
    
    # Workflow coordination
    final_response: str
    workflow_status: str        # "in_progress" | "completed" | "error" | "paused_approval"
    tool_errors: List[str]
    approval_status: Optional[str]
