"""
Session memory manager for Athena.
Ensures session isolation, supports conversation reset/clearing, and interfaces with checkpointing.
"""
import logging
from typing import Dict, List, Optional
from app.models.schemas import ChatMessage, MessageRole
from app.memory.summarizer import compress_history_if_needed

logger = logging.getLogger(__name__)

class SessionMemoryManager:
    def __init__(self):
        # In-memory session message store: {session_id: List[ChatMessage]}
        self._sessions: Dict[str, List[ChatMessage]] = {}
        # Session owner mapping: {session_id: user_id}
        self._session_owners: Dict[str, str] = {}
        # Session topics: {session_id: str}
        self._session_topics: Dict[str, str] = {}

    def get_session_messages(self, session_id: str, user_id: str = "guest") -> List[ChatMessage]:
        """Returns messages for a session. Enforces user ownership check."""
        owner = self._session_owners.get(session_id)
        if owner and owner != user_id:
            logger.warning(f"Unauthorized session access attempt: User {user_id} tried to read session {session_id} owned by {owner}")
            raise PermissionError(f"Access denied: Session belongs to another learner.")
        
        return list(self._sessions.get(session_id, []))

    def add_message(self, session_id: str, message: ChatMessage, user_id: str = "guest", active_topic: str = "Computer Science") -> None:
        """Appends a message, registering owner and managing token compression."""
        owner = self._session_owners.get(session_id)
        if owner and owner != user_id:
            raise PermissionError(f"Access denied: Cannot append to another learner's session.")
        
        self._session_owners[session_id] = user_id
        if session_id not in self._sessions:
            self._sessions[session_id] = []
            
        self._sessions[session_id].append(message)
        self._session_topics[session_id] = active_topic

        # Check for context compression
        compressed, was_compressed = compress_history_if_needed(
            self._sessions[session_id],
            active_topic=active_topic
        )
        if was_compressed:
            self._sessions[session_id] = compressed

    def clear_session(self, session_id: str, user_id: str = "guest") -> bool:
        """Clears messages for a session while verifying ownership."""
        owner = self._session_owners.get(session_id)
        if owner and owner != user_id:
            raise PermissionError(f"Access denied: Cannot clear another learner's session.")
        
        if session_id in self._sessions:
            self._sessions[session_id] = []
            return True
        return False

    def get_topic(self, session_id: str) -> str:
        return self._session_topics.get(session_id, "Computer Science")

    def set_topic(self, session_id: str, topic: str):
        self._session_topics[session_id] = topic

session_memory = SessionMemoryManager()
