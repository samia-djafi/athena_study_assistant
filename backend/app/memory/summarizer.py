"""
Long-conversation management and summarization for Athena.
Maintains token boundaries, summarizes older messages, and preserves critical learning context.
"""
import logging
from typing import List, Dict, Any, Tuple
from app.models.schemas import ChatMessage, MessageRole
from app.config import settings

logger = logging.getLogger(__name__)

def estimate_tokens(text: str) -> int:
    """Rough token estimation (~4 chars per token)."""
    return max(1, len(text) // 4)

def count_conversation_tokens(messages: List[ChatMessage]) -> int:
    return sum(estimate_tokens(m.content) for m in messages)

def compress_history_if_needed(
    messages: List[ChatMessage],
    active_topic: str,
    max_tokens: int = settings.MAX_CONVERSATION_TOKENS,
    threshold: int = settings.SUMMARY_THRESHOLD_TOKENS
) -> Tuple[List[ChatMessage], bool]:
    """
    Checks if conversation exceeds context threshold.
    If so, compresses older history into a structured executive context block
    while keeping the most recent 4 messages untouched.
    """
    total = count_conversation_tokens(messages)
    if total <= threshold or len(messages) <= 6:
        return messages, False

    logger.info(f"Conversation token limit approached ({total} tokens). Summarizing earlier messages.")
    
    # Keep the recent messages
    recent_count = 4
    older_messages = messages[:-recent_count]
    recent_messages = messages[-recent_count:]
    
    # Extract topics and key inquiries from older messages
    user_queries = [m.content[:80] for m in older_messages if m.role == MessageRole.USER]
    topics_covered = set()
    for q in user_queries:
        for word in q.split():
            if len(word) > 4:
                topics_covered.add(word)
                
    summary_content = (
        f"--- CONVERSATION CONTEXT SUMMARY ---\n"
        f"Current Learning Topic: {active_topic}\n"
        f"Key prior concepts discussed: {', '.join(list(topics_covered)[:6]) or 'Fundamentals'}\n"
        f"Total historical messages summarized: {len(older_messages)}\n"
        f"Status: Active study thread continues below."
    )
    
    summary_message = ChatMessage(
        role=MessageRole.SYSTEM,
        content=summary_content,
        metadata={"is_summary": True, "summarized_count": len(older_messages)}
    )
    
    compressed = [summary_message] + recent_messages
    return compressed, True
