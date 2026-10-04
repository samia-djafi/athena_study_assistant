"""
Coding Agent for Athena AI/CS Study Assistant.
Provides static code analysis, algorithm complexity estimation, bug identification, and debugging guidance.
STRICT SAFETY GUARANTEE: Never executes arbitrary code on the host machine.
"""
import re
import logging
from typing import Dict, Any, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AthenaState
from app.agents.llm_factory import get_llm
from app.tools.code_analyzer import analyze_python_code
from app.models.schemas import CodeAnalysisResult

logger = logging.getLogger(__name__)

CODING_SYSTEM_PROMPT = """You are Athena's Coding Agent, a specialist in programming, software engineering, and algorithm analysis.

Your responsibilities:
1. Provide pedagogical explanations of source code, algorithms, and design patterns.
2. Explain syntax errors, exceptions, and stack traces with actionable step-by-step solutions.
3. Analyze time and space complexity with Big-O notation.
4. Provide idiomatic, clean code snippets with clear inline comments.
5. Emphasize that all code review is STATIC analysis. Clearly distinguish between generated code and statically reviewed code.
"""

def extract_code_block(text: str) -> Optional[str]:
    """Extracts first code block enclosed in ```python ... ``` or ``` ... ```."""
    pattern = r"```(?:python)?\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    return None

async def run_coding_agent(state: AthenaState) -> AthenaState:
    """
    Executes the Coding Agent node in the LangGraph workflow.
    """
    query = state.get("current_request", "")
    logger.info("Coding Agent invoked.")

    state["active_agent"] = "Coding Agent"
    if "requested_agents" not in state:
        state["requested_agents"] = []
    if "Coding Agent" not in state["requested_agents"]:
        state["requested_agents"].append("Coding Agent")

    # Extract code if student provided any in query
    extracted_code = extract_code_block(query)
    analysis_result: Optional[CodeAnalysisResult] = None
    
    if extracted_code:
        # Perform safe static AST analysis
        analysis_result = analyze_python_code(extracted_code)
        state["coding_output"] = analysis_result.model_dump()
    else:
        # User is asking a coding question or concept
        analysis_result = CodeAnalysisResult(
            language="python",
            is_safe=True,
            static_summary="Conceptual programming inquiry without inline code block.",
            ast_valid=True,
            complexity=None,
            suggested_fixes=[],
            has_executed=False
        )
        state["coding_output"] = analysis_result.model_dump()

    llm = get_llm()
    system_msg = SystemMessage(content=CODING_SYSTEM_PROMPT)
    user_prompt = f"User Inquiry:\n{query}\n\n"
    if extracted_code and analysis_result:
        user_prompt += (
            f"Static Analysis Summary (NO EXECUTION ON HOST):\n"
            f"- AST Valid: {analysis_result.ast_valid}\n"
            f"- Estimated Complexity: {analysis_result.complexity}\n"
            f"- Static Summary: {analysis_result.static_summary}\n"
            f"- Notices: {', '.join(analysis_result.suggested_fixes) or 'None'}\n"
        )

    try:
        response = await llm.ainvoke([system_msg, HumanMessage(content=user_prompt)])
        output_text = response.content
    except Exception as e:
        logger.error(f"Coding Agent LLM invocation failed: {e}")
        output_text = (
            f"### Static Code Review\n\n"
            f"{analysis_result.static_summary}\n\n"
            f"**Security & Execution Notice**: Code was analyzed statically via AST; no untrusted code was executed."
        )

    # Append static execution notice
    output_text += "\n\n> 🛡️ *Note: This code was analyzed via safe static analysis. Athena isolates the backend and does not execute arbitrary user code on the host machine.*"

    state["final_response"] = output_text
    return state
