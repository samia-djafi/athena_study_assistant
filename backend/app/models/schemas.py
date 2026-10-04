"""
Pydantic schemas and data models for Athena.
"""
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
import time
import uuid

class LearningLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ExplanationDepth(str, Enum):
    SHORT = "short"
    STANDARD = "standard"
    DETAILED = "detailed"

class TaskType(str, Enum):
    DEFINITION = "definition"
    TUTOR = "tutor"
    RESEARCH = "research"
    CODING = "coding"
    ASSESSMENT = "assessment"
    KNOWLEDGE_RAG = "knowledge_rag"
    GENERAL = "general"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    timestamp: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WebSource(BaseModel):
    title: str
    url: str
    snippet: str
    publication_date: Optional[str] = None
    source_domain: Optional[str] = None

class CodeAnalysisResult(BaseModel):
    language: str
    is_safe: bool = True
    static_summary: str
    ast_valid: bool = True
    complexity: Optional[str] = None
    suggested_fixes: List[str] = Field(default_factory=list)
    has_executed: bool = False  # Strict safety guarantee

class QuizType(str, Enum):
    MCQ = "multiple_choice"
    CONCEPTUAL = "conceptual"
    CODING = "coding"

class QuizQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    type: QuizType = QuizType.MCQ
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str

class QuizGenerateRequest(BaseModel):
    topic: str
    learning_level: LearningLevel = LearningLevel.INTERMEDIATE
    count: int = 3
    type: QuizType = QuizType.MCQ

class QuizGenerateResponse(BaseModel):
    quiz_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    learning_level: LearningLevel
    questions: List[QuizQuestion]

class QuizAnswerSubmission(BaseModel):
    question_id: str
    selected_answer: str

class QuizSubmissionRequest(BaseModel):
    quiz_id: str
    topic: str
    user_id: str = "guest"
    answers: List[QuizAnswerSubmission]

class QuizEvaluationItem(BaseModel):
    question_id: str
    question_text: str
    selected_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str

class QuizSubmissionResponse(BaseModel):
    quiz_id: str
    score: int
    total: int
    percentage: float
    evaluations: List[QuizEvaluationItem]
    knowledge_gaps: List[str]
    recommended_revision: List[str]

class DocumentStatus(str, Enum):
    UPLOADED = "Uploaded"
    PROCESSING = "Processing"
    READY = "Ready"
    FAILED = "Failed"

class DocumentItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "guest"
    filename: str
    file_type: str
    size_bytes: int
    status: DocumentStatus = DocumentStatus.READY
    uploaded_at: float = Field(default_factory=time.time)
    note: str = "RAG UI prototype — backend indexing not implemented"

class LearnerProfile(BaseModel):
    user_id: str = "guest"
    preferred_level: LearningLevel = LearningLevel.INTERMEDIATE
    preferred_depth: ExplanationDepth = ExplanationDepth.STANDARD
    preferred_language: str = "English"
    recently_studied_topics: List[str] = Field(default_factory=lambda: [
        "Data Structures: Binary Search Trees",
        "Transformer Attention Mechanisms",
        "Asynchronous Python & Concurrency"
    ])
    learning_goals: List[str] = Field(default_factory=lambda: [
        "Master Deep Learning Foundations",
        "Prepare for Technical Systems Interviews"
    ])
    total_study_sessions: int = 4
    total_quizzes_taken: int = 3
    average_quiz_score: float = 85.0
    topics_to_review: List[str] = Field(default_factory=lambda: [
        "Dynamic Programming: Memoization vs Tabulation",
        "Graph Traversal Complexity"
    ])

class ChatRequest(BaseModel):
    message: str
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "guest"
    learning_level: LearningLevel = LearningLevel.INTERMEDIATE
    explanation_depth: ExplanationDepth = ExplanationDepth.STANDARD
    learning_goal: Optional[str] = None
    image_data: Optional[str] = None  # Base64 or URL
    audio_transcription: Optional[str] = None
    require_search: Optional[bool] = None

class AgentActivity(BaseModel):
    agent_name: str
    status: str
    timestamp: float = Field(default_factory=time.time)

class ChatResponse(BaseModel):
    session_id: str
    response: str
    active_agent: str
    agents_involved: List[str]
    sources: List[WebSource] = Field(default_factory=list)
    code_analysis: Optional[CodeAnalysisResult] = None
    approval_required: bool = False
    approval_token: Optional[str] = None
    approval_action: Optional[str] = None

class StreamChunk(BaseModel):
    type: str  # "status", "token", "source", "done", "error", "approval"
    agent: Optional[str] = None
    content: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class ApprovalDecisionRequest(BaseModel):
    session_id: str
    approval_token: str
    approved: bool

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    environment: str
    llm_provider: str
    database: str
    mcp_enabled: bool
