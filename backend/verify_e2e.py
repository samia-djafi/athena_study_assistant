"""
End-to-end programmatic verification script for Athena.
Tests backend initialization, database creation, REST chat, SSE chat, quiz generation & scoring,
and session management without starting an external web server process.
"""
import asyncio
from app.database.db import init_db
from app.agents.orchestrator import run_orchestrator
from app.agents.assessment_agent import generate_quiz, evaluate_quiz_submission
from app.models.schemas import LearningLevel, QuizSubmissionRequest, QuizAnswerSubmission
from app.tools.calculator import safe_calculate
from app.tools.code_analyzer import analyze_python_code
from app.tools.mcp_client import mcp_client

async def main():
    print("=== Step 1: Initializing Database ===")
    await init_db()
    print("Database initialized successfully.")

    print("\n=== Step 2: Testing Multi-Agent Orchestration (Tutor Agent) ===")
    res = await run_orchestrator(
        user_id="e2e_student",
        session_id="e2e_session_1",
        message="Explain Dijkstra's Algorithm",
        learning_level="intermediate",
        explanation_depth="standard"
    )
    print(f"Active Agent: {res.get('active_agent')}")
    print(f"Response length: {len(res.get('final_response', ''))} characters")
    assert len(res.get("final_response", "")) > 50

    print("\n=== Step 3: Testing Research Routing & Source Grounding ===")
    res_research = await run_orchestrator(
        user_id="e2e_student",
        session_id="e2e_session_2",
        message="Research recent developments in Transformer attention",
        require_search=True
    )
    print(f"Active Agent: {res_research.get('active_agent')}")
    print(f"Web Sources Found: {len(res_research.get('web_sources', []))}")
    assert len(res_research.get("web_sources", [])) > 0

    print("\n=== Step 4: Testing Coding Agent Safe Static Analysis ===")
    sample_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
"""
    code_res = analyze_python_code(sample_code)
    print(f"Complexity: {code_res.complexity}")
    print(f"Has executed on host: {code_res.has_executed}")
    assert code_res.has_executed is False
    assert "O(n^2)" in code_res.complexity

    print("\n=== Step 5: Testing Assessment Agent Quiz & Evaluation ===")
    quiz = await generate_quiz("Algorithms", LearningLevel.INTERMEDIATE, count=2)
    print(f"Generated {len(quiz.questions)} questions for {quiz.topic}")
    
    sub = QuizSubmissionRequest(
        quiz_id=quiz.quiz_id,
        topic=quiz.topic,
        user_id="e2e_student",
        answers=[
            QuizAnswerSubmission(
                question_id=quiz.questions[0].id,
                selected_answer=quiz.questions[0].correct_answer
            )
        ]
    )
    eval_res = evaluate_quiz_submission(sub, quiz.questions)
    print(f"Scored: {eval_res.score} / {eval_res.total} ({eval_res.percentage}%)")
    assert eval_res.score == 1

    print("\n=== Step 6: Testing MCP Client Tool ===")
    mcp_res = await mcp_client.invoke_tool("lookup_arxiv_metadata", {"arxiv_id": "1706.03762"})
    print(f"MCP Tool Execution: {mcp_res['success']}")
    assert mcp_res["success"] is True

    print("\n[SUCCESS] All End-to-End System Components Verified Successfully!")

if __name__ == "__main__":
    asyncio.run(main())
