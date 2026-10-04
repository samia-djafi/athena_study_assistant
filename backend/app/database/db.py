"""
Database layer for Athena.
Supports local SQLite via aiosqlite and SQLAlchemy, and is structured for seamless Supabase PostgreSQL migration.
"""
import time
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from app.config import settings
from app.models.schemas import (
    LearningLevel, ExplanationDepth, DocumentStatus,
    LearnerProfile, DocumentItem, ChatMessage, MessageRole
)

Base = declarative_base()

class DBUser(Base):
    __tablename__ = "users"
    id = Column(String(64), primary_key=True)
    username = Column(String(64), default="learner")
    created_at = Column(Float, default=time.time)
    
    preferences = relationship("DBLearnerPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("DBSession", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("DBDocument", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("DBQuizAttempt", back_populates="user", cascade="all, delete-orphan")

class DBLearnerPreference(Base):
    __tablename__ = "learner_preferences"
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), ForeignKey("users.id"), unique=True, nullable=False)
    preferred_level = Column(String(32), default=LearningLevel.INTERMEDIATE.value)
    preferred_depth = Column(String(32), default=ExplanationDepth.STANDARD.value)
    preferred_language = Column(String(32), default="English")
    recently_studied = Column(JSON, default=list)
    learning_goals = Column(JSON, default=list)
    topics_to_review = Column(JSON, default=list)
    total_study_sessions = Column(Integer, default=0)
    
    user = relationship("DBUser", back_populates="preferences")

class DBSession(Base):
    __tablename__ = "sessions"
    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), default="New Learning Session")
    topic = Column(String(255), default="Computer Science")
    created_at = Column(Float, default=time.time)
    updated_at = Column(Float, default=time.time)
    summary = Column(Text, nullable=True)
    
    user = relationship("DBUser", back_populates="sessions")
    messages = relationship("DBMessage", back_populates="session", cascade="all, delete-orphan", order_by="DBMessage.timestamp")

class DBMessage(Base):
    __tablename__ = "messages"
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), ForeignKey("sessions.id"), nullable=False)
    role = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(Float, default=time.time)
    metadata_json = Column(JSON, default=dict)
    
    session = relationship("DBSession", back_populates="messages")

class DBDocument(Base):
    __tablename__ = "documents"
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(64), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    status = Column(String(32), default=DocumentStatus.READY.value)
    uploaded_at = Column(Float, default=time.time)
    note = Column(String(255), default="RAG UI prototype — backend indexing not implemented")
    
    user = relationship("DBUser", back_populates="documents")

class DBQuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    topic = Column(String(255), nullable=False)
    score = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    evaluations_json = Column(JSON, default=list)
    knowledge_gaps_json = Column(JSON, default=list)
    recommended_revision_json = Column(JSON, default=list)
    created_at = Column(Float, default=time.time)
    
    user = relationship("DBUser", back_populates="quiz_attempts")

# Engine & Session Factory
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Seed default user if not exists
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(DBUser).where(DBUser.id == "guest"))
        user = result.scalar_one_or_none()
        if not user:
            user = DBUser(id="guest", username="Athena Learner")
            session.add(user)
            pref = DBLearnerPreference(
                user_id="guest",
                preferred_level=LearningLevel.INTERMEDIATE.value,
                preferred_depth=ExplanationDepth.STANDARD.value,
                recently_studied=["Data Structures: Trees", "Attention Mechanisms"],
                learning_goals=["AI System Design", "Algorithms Mastery"],
                topics_to_review=["Dynamic Programming", "Graph Traversal"],
                total_study_sessions=3
            )
            session.add(pref)
            await session.commit()

async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session

# Helper Database Operations
async def get_or_create_user(session: AsyncSession, user_id: str = "guest") -> DBUser:
    result = await session.execute(select(DBUser).where(DBUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        user = DBUser(id=user_id, username=f"User {user_id}")
        session.add(user)
        pref = DBLearnerPreference(user_id=user_id)
        session.add(pref)
        await session.commit()
        await session.refresh(user)
    return user

async def get_session_history(session: AsyncSession, session_id: str) -> List[ChatMessage]:
    result = await session.execute(
        select(DBMessage).where(DBMessage.session_id == session_id).order_by(DBMessage.timestamp)
    )
    db_msgs = result.scalars().all()
    return [
        ChatMessage(
            id=m.id,
            role=MessageRole(m.role),
            content=m.content,
            timestamp=m.timestamp,
            metadata=m.metadata_json or {}
        )
        for m in db_msgs
    ]

async def save_message(session: AsyncSession, session_id: str, role: str, content: str, user_id: str = "guest", metadata: Optional[Dict[str, Any]] = None):
    # Ensure session exists
    res = await session.execute(select(DBSession).where(DBSession.id == session_id))
    db_sess = res.scalar_one_or_none()
    if not db_sess:
        await get_or_create_user(session, user_id)
        title = content[:40] + "..." if len(content) > 40 else content
        db_sess = DBSession(id=session_id, user_id=user_id, title=title)
        session.add(db_sess)
    
    db_sess.updated_at = time.time()
    msg = DBMessage(
        session_id=session_id,
        role=role,
        content=content,
        metadata_json=metadata or {}
    )
    session.add(msg)
    await session.commit()
