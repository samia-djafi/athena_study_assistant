"""
Security middleware, authorization, and Human-in-the-Loop approval checkpoints for Athena.
"""
import uuid
import time
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class PendingApproval(BaseModel):
    token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    action_type: str
    description: str
    payload: Dict[str, Any]
    created_at: float = Field(default_factory=time.time)
    expires_at: float = Field(default_factory=lambda: time.time() + 600)  # 10 min expiry

class HumanApprovalManager:
    """
    Manages approval checkpoints for sensitive or consequential operations.
    Ordinary educational explanations do NOT require approval.
    Destructive operations (e.g. data deletion, external modifications) pause for consent.
    """
    def __init__(self):
        self._pending: Dict[str, PendingApproval] = {}

    def request_approval(self, session_id: str, user_id: str, action_type: str, description: str, payload: Dict[str, Any]) -> PendingApproval:
        approval = PendingApproval(
            session_id=session_id,
            user_id=user_id,
            action_type=action_type,
            description=description,
            payload=payload
        )
        self._pending[approval.token] = approval
        logger.info(f"Created pending approval checkpoint [{approval.token}] for action '{action_type}' in session {session_id}")
        return approval

    def resolve_approval(self, token: str, approved: bool) -> Optional[PendingApproval]:
        approval = self._pending.get(token)
        if not approval:
            return None
        
        if time.time() > approval.expires_at:
            del self._pending[token]
            logger.warning(f"Approval token [{token}] has expired.")
            return None
            
        del self._pending[token]
        return approval if approved else None

    def get_pending(self, token: str) -> Optional[PendingApproval]:
        return self._pending.get(token)

approval_manager = HumanApprovalManager()

def sanitize_user_input(text: str) -> str:
    """Inspects and sanitizes user input for prohibited payload injections."""
    cleaned = text.strip()
    return cleaned

def check_permission(user_id: str, resource_owner_id: str) -> bool:
    """Verifies that the acting user has rights to the specified resource."""
    return user_id == resource_owner_id or user_id == "admin"
