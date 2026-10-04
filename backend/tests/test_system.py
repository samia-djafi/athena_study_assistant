"""
Automated system, security, and integration tests for Athena.
Covers:
- Test 4: Follow-up question retains session context.
- Test 5: Session isolation (no cross-session data leakage).
- Test 12: Failed tools produce useful error handling.
- Test 13: Long conversations managed within context limits.
- Test 14: Unauthorized access refusal.
- Test 15: Streaming & error handling.
- Test 16: Uploaded file validation.
- Test 17: Human approval checkpoint pause and resume.
"""
import pytest
import asyncio
from app.memory.session_memory import session_memory
from app.models.schemas import ChatMessage, MessageRole, ChatRequest
from app.memory.summarizer import compress_history_if_needed, estimate_tokens
from app.middleware.security import approval_manager, check_permission
from app.multimodal.vision import validate_image_data
from app.tools.calculator import safe_calculate
from app.agents.orchestrator import run_orchestrator
from app.api.chat import post_chat_stream

@pytest.mark.asyncio
async def test_04_followup_question_retains_context():
    """Test 4: A follow-up question retains the appropriate session context."""
    sess_id = "session_context_test"
    session_memory.clear_session(sess_id, user_id="student_1")

    # First turn
    msg1 = ChatMessage(role=MessageRole.USER, content="Let's study Quicksort algorithms.")
    session_memory.add_message(sess_id, msg1, user_id="student_1", active_topic="Quicksort")

    # Second turn
    msg2 = ChatMessage(role=MessageRole.USER, content="What is its worst-case complexity?")
    session_memory.add_message(sess_id, msg2, user_id="student_1", active_topic="Quicksort")

    history = session_memory.get_session_messages(sess_id, user_id="student_1")
    assert len(history) == 2
    assert session_memory.get_topic(sess_id) == "Quicksort"

@pytest.mark.asyncio
async def test_05_sessions_do_not_share_memory():
    """Test 5: Two different sessions do not share private memory."""
    sess_a = "session_alice"
    sess_b = "session_bob"

    session_memory.add_message(sess_a, ChatMessage(role=MessageRole.USER, content="Alice's private research"), user_id="alice")
    session_memory.add_message(sess_b, ChatMessage(role=MessageRole.USER, content="Bob's private research"), user_id="bob")

    alice_history = session_memory.get_session_messages(sess_a, user_id="alice")
    bob_history = session_memory.get_session_messages(sess_b, user_id="bob")

    assert len(alice_history) == 1
    assert "Alice" in alice_history[0].content
    assert "Bob" not in alice_history[0].content

    # Unauthorized access check
    with pytest.raises(PermissionError):
        session_memory.get_session_messages(sess_a, user_id="bob")

@pytest.mark.asyncio
async def test_12_failed_tools_produce_useful_error():
    """Test 12: Failed tools produce useful error handling."""
    # Calculator division by zero
    res = safe_calculate("10 / 0")
    assert res["success"] is False
    assert "division by zero" in res["error"].lower()

    # Calculator disallowed identifier
    res2 = safe_calculate("malicious_eval(5)")
    assert res2["success"] is False
    assert "not in the safe calculation whitelist" in res2["error"] or "Undefined" in res2["error"]

@pytest.mark.asyncio
async def test_13_long_conversations_managed_in_context():
    """Test 13: Long conversations are managed within configured context limits."""
    large_messages = []
    # Build 12 messages with large content
    for i in range(12):
        large_messages.append(ChatMessage(
            role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
            content=f"Step {i}: In-depth explanation of compiler design, AST construction, and symbol tables " * 40
        ))

    compressed, was_compressed = compress_history_if_needed(
        large_messages,
        active_topic="Compilers",
        max_tokens=2000,
        threshold=1000
    )
    assert was_compressed is True
    assert len(compressed) < len(large_messages)
    assert compressed[0].role == MessageRole.SYSTEM
    assert "CONTEXT SUMMARY" in compressed[0].content

@pytest.mark.asyncio
async def test_14_unauthorized_access_refusal():
    """Test 14: Unauthorized requests cannot access private documents or sessions."""
    assert check_permission("alice", "alice") is True
    assert check_permission("eve", "alice") is False
    assert check_permission("admin", "alice") is True

@pytest.mark.asyncio
async def test_15_streaming_response():
    """Test 15: Streaming SSE response produces valid chunk events."""
    req = ChatRequest(
        message="What is dynamic programming?",
        session_id="stream_test_sess",
        user_id="test_user"
    )
    streaming_resp = await post_chat_stream(req)
    assert streaming_resp.status_code == 200
    assert streaming_resp.media_type == "text/event-stream"

@pytest.mark.asyncio
async def test_16_file_upload_validation():
    """Test 16: Uploaded files and images are properly validated."""
    # Invalid image MIME
    bad_img = "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg=="
    val = validate_image_data(bad_img)
    assert val["valid"] is False
    assert "Unsupported image MIME type" in val["error"]

    # Valid PNG image mock data
    valid_png = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    val_ok = validate_image_data(valid_png)
    assert val_ok["valid"] is True

@pytest.mark.asyncio
async def test_17_human_approval_checkpoints():
    """Test 17: Human approval checkpoints pause and resume correctly."""
    approval = approval_manager.request_approval(
        session_id="sess_sensitive",
        user_id="student_1",
        action_type="DELETE_ALL_LEARNING_HISTORY",
        description="Consent required to clear complete learner study records.",
        payload={"target": "all"}
    )
    assert approval.token is not None
    assert approval_manager.get_pending(approval.token) is not None

    # Resume when user approves
    resolved = approval_manager.resolve_approval(approval.token, approved=True)
    assert resolved is not None
    assert resolved.action_type == "DELETE_ALL_LEARNING_HISTORY"
    # Token should be consumed
    assert approval_manager.get_pending(approval.token) is None

@pytest.mark.asyncio
async def test_18_mcp_client_tool_invocation():
    """Test 18: MCP client registers tools and executes safely with timeout boundaries."""
    from app.tools.mcp_client import mcp_client
    tools = mcp_client.list_available_tools()
    assert len(tools) > 0
    assert any(t.name == "lookup_arxiv_metadata" for t in tools)

    res = await mcp_client.invoke_tool("lookup_arxiv_metadata", {"arxiv_id": "1706.03762"})
    assert res["success"] is True
    assert "Attention Is All You Need" in res["result"]["title"]

