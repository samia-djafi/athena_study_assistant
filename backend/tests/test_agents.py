"""
Automated unit & integration tests for Athena Specialized Agents.
Covers:
- Test 1: Model responds to basic educational question.
- Test 2: Tutor Agent respects selected explanation depth (short vs detailed).
- Test 3: Tool can be called and result is used correctly (Calculator).
- Test 6: Research Agent returns grounded source metadata.
- Test 7 & 8: Knowledge Agent prototype behavior & refusal to invent document citations.
- Test 9: Coding Agent does not execute arbitrary code in main backend.
- Test 10: Assessment Agent produces valid structured questions.
- Test 11: Orchestrator selects appropriate agents for different requests.
"""
import pytest
import asyncio
from app.agents.orchestrator import run_orchestrator, router_condition
from app.agents.tutor_agent import run_tutor_agent
from app.agents.research_agent import run_research_agent
from app.agents.coding_agent import run_coding_agent
from app.agents.assessment_agent import generate_quiz, evaluate_quiz_submission, run_assessment_agent
from app.agents.knowledge_agent import run_knowledge_agent
from app.tools.calculator import safe_calculate
from app.tools.code_analyzer import analyze_python_code
from app.models.schemas import LearningLevel, ExplanationDepth, QuizSubmissionRequest, QuizAnswerSubmission

@pytest.mark.asyncio
async def test_01_basic_educational_question():
    """Test 1: The model responds to a basic educational question."""
    res = await run_orchestrator(
        user_id="test_user",
        session_id="test_sess_01",
        message="What is a Binary Search Tree?",
        learning_level="intermediate",
        explanation_depth="standard"
    )
    assert res.get("workflow_status") == "completed"
    assert len(res.get("final_response", "")) > 20
    assert "Binary Search" in res["final_response"] or "Tree" in res["final_response"]

@pytest.mark.asyncio
async def test_02_tutor_respects_depth():
    """Test 2: The Tutor Agent respects the selected explanation depth."""
    # Short depth
    short_state = {
        "current_request": "Explain Binary Search",
        "current_topic": "Binary Search",
        "learning_level": "intermediate",
        "explanation_depth": "short"
    }
    short_res = await run_tutor_agent(short_state)
    short_len = len(short_res["final_response"])

    # Detailed depth
    detailed_state = {
        "current_request": "Explain Binary Search",
        "current_topic": "Binary Search",
        "learning_level": "advanced",
        "explanation_depth": "detailed"
    }
    detailed_res = await run_tutor_agent(detailed_state)
    detailed_len = len(detailed_res["final_response"])

    assert detailed_len > short_len * 2
    assert "O(log n)" in detailed_res["final_response"] or "O(" in short_res["final_response"]

@pytest.mark.asyncio
async def test_03_tool_invocation_calculator():
    """Test 3: A tool can be called and its result is used correctly."""
    calc_res = safe_calculate("2 ** 10 + 24")
    assert calc_res["success"] is True
    assert calc_res["result"] == 1048

    # Safe error on invalid/malicious input
    bad_calc = safe_calculate("__import__('os').system('ls')")
    assert bad_calc["success"] is False
    assert bad_calc["result"] is None

@pytest.mark.asyncio
async def test_06_research_agent_source_metadata():
    """Test 6: The Research Agent returns grounded source metadata."""
    state = {
        "current_request": "Research transformer attention mechanism",
        "current_topic": "Transformer Attention",
        "requested_agents": []
    }
    res = await run_research_agent(state)
    assert "web_sources" in res
    assert len(res["web_sources"]) > 0
    first_src = res["web_sources"][0]
    assert "title" in first_src
    assert "url" in first_src
    assert "source_domain" in first_src
    assert first_src["url"].startswith("http")

@pytest.mark.asyncio
async def test_07_and_08_knowledge_agent_refuses_hallucinating_citations():
    """Test 7 & 8: The Knowledge Agent adheres to RAG UI prototype and refuses to invent citations."""
    state = {
        "current_request": "What does my uploaded document say about page 4?",
        "current_topic": "Document Notes",
        "requested_agents": []
    }
    res = await run_knowledge_agent(state)
    assert res["active_agent"] == "Knowledge Agent"
    assert res["retrieved_documents"] == []
    assert "UI Prototype" in res["final_response"]
    assert "refuses to fabricate" in res["final_response"]

@pytest.mark.asyncio
async def test_09_coding_agent_static_analysis_safe_guarantee():
    """Test 9: The Coding Agent does not execute arbitrary code in the main backend."""
    unsafe_code = """
import os
import subprocess

def dangerous_function():
    os.system("rm -rf /")
    return "done"
"""
    analysis = analyze_python_code(unsafe_code)
    # Verification: AST ran statically, has_executed is False, sensitive calls flagged
    assert analysis.has_executed is False
    assert analysis.is_safe is False
    assert any("Restricted" in fix or "Sensitive" in fix or "dangerous" in fix.lower() for fix in analysis.suggested_fixes)

    # Complexity heuristic test
    nested_loop_code = """
for i in range(n):
    for j in range(n):
        print(i, j)
"""
    nested_analysis = analyze_python_code(nested_loop_code)
    assert nested_analysis.has_executed is False
    assert "O(n^2)" in nested_analysis.complexity

@pytest.mark.asyncio
async def test_10_assessment_agent_structured_questions():
    """Test 10: The Assessment Agent produces valid structured questions and evaluates answers."""
    quiz_res = await generate_quiz("Binary Search Trees", LearningLevel.INTERMEDIATE, count=2)
    assert len(quiz_res.questions) == 2
    assert quiz_res.questions[0].correct_answer is not None
    assert len(quiz_res.questions[0].options) > 2

    # Test evaluation submission
    sub = QuizSubmissionRequest(
        quiz_id=quiz_res.quiz_id,
        topic="Binary Search Trees",
        user_id="test_user",
        answers=[
            QuizAnswerSubmission(
                question_id=quiz_res.questions[0].id,
                selected_answer=quiz_res.questions[0].correct_answer
            )
        ]
    )
    eval_res = evaluate_quiz_submission(sub, quiz_res.questions)
    assert eval_res.score >= 1
    assert eval_res.percentage > 0.0
    assert len(eval_res.evaluations) >= 1

@pytest.mark.asyncio
async def test_11_orchestrator_conditional_routing():
    """Test 11: The orchestrator selects appropriate agents for different requests."""
    # Routing to Assessment
    assert router_condition({"current_request": "Give me a quiz on data structures"}) == "assessment"
    
    # Routing to Coding
    assert router_condition({"current_request": "Why does this python function throw a SyntaxError?"}) == "coding"
    
    # Routing to Knowledge
    assert router_condition({"current_request": "What does my uploaded document say?"}) == "knowledge"
    
    # Routing to Research
    assert router_condition({"current_request": "Search the web for recent arxiv papers on transformers"}) == "research"
    
    # Routing to Tutor
    assert router_condition({"current_request": "Can you explain what recursion means?"}) == "tutor"
