"""
Central Orchestrator Agent for Athena AI/CS Study Assistant.
Built as a stateful LangGraph workflow with conditional routing and checkpointing.
"""
import re
import logging
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.state import AthenaState
from app.agents.tutor_agent import run_tutor_agent
from app.agents.research_agent import run_research_agent
from app.agents.coding_agent import run_coding_agent
from app.agents.assessment_agent import run_assessment_agent
from app.agents.knowledge_agent import run_knowledge_agent
from app.tools.calculator import safe_calculate

logger = logging.getLogger(__name__)

def classify_intent_node(state: AthenaState) -> AthenaState:
    """
    Analyzes the student's request, inspects active context,
    and initializes orchestrator routing metadata.
    """
    req = state.get("current_request", "").strip()
    req_lower = req.lower()
    
    # Extract topic heuristic
    topic = state.get("current_topic")
    if not topic or topic == "Computer Science":
        # Heuristic topic extraction
        words = [w for w in re.findall(r'\b[A-Za-z0-9_-]+\b', req) if len(w) > 3 and w.lower() not in {"what", "how", "explain", "please", "about", "with", "from", "that", "this"}]
        topic = " ".join(words[:3]) if words else "Computer Science"
        state["current_topic"] = topic

    # Check for direct calculation inquiry
    calc_match = re.search(r'(?:calculate|compute|what is)\s+([0-9\+\-\*\/\^\(\)\.\s\w]+)', req_lower)
    if calc_match and any(op in calc_match.group(1) for op in ["+", "-", "*", "/", "^"]):
        expr = calc_match.group(1).replace("what is", "").strip()
        calc_res = safe_calculate(expr)
        if calc_res.get("success"):
            state["relevant_memory"] = state.get("relevant_memory", {})
            state["relevant_memory"]["last_calc"] = calc_res

    state["active_agent"] = "Orchestrator Agent"
    state["requested_agents"] = ["Orchestrator Agent"]
    state["workflow_status"] = "in_progress"
    return state

def router_condition(state: AthenaState) -> Literal["research", "knowledge", "coding", "assessment", "tutor"]:
    """
    Conditional routing edge logic:
    Selects the appropriate specialized agent based on task requirements.
    """
    req = state.get("current_request", "").lower()
    explicit_search = state.get("relevant_memory", {}).get("require_search", False)

    # 1. Assessment / Quiz requests
    if any(k in req for k in ["quiz", "assessment", "test my", "practice questions", "exercise", "exam"]):
        return "assessment"

    # 2. Uploaded Document / RAG requests
    if any(k in req for k in ["uploaded document", "my pdf", "my notes", "in the file", "from the document"]):
        return "knowledge"

    # 3. Coding / Debugging / Implementation requests
    if (
        "```" in state.get("current_request", "") or
        any(k in req for k in ["debug", "code", "python error", "stack trace", "syntaxerror", "complexity of this code", "write a function", "implement in python", "traceback"])
    ):
        return "coding"

    # 4. Explicit or implicit research requests
    if explicit_search or any(k in req for k in ["research", "search the web", "latest sources", "recent papers", "arxiv", "external docs", "documentation for"]):
        return "research"

    # 5. Default educational tutoring
    return "tutor"

def build_orchestrator_graph():
    """
    Constructs the LangGraph stateful multi-agent workflow.
    """
    workflow = StateGraph(AthenaState)

    # Add Nodes
    workflow.add_node("classify", classify_intent_node)
    workflow.add_node("research", run_research_agent)
    workflow.add_node("tutor", run_tutor_agent)
    workflow.add_node("coding", run_coding_agent)
    workflow.add_node("assessment", run_assessment_agent)
    workflow.add_node("knowledge", run_knowledge_agent)

    # Entry edge
    workflow.add_edge(START, "classify")

    # Conditional branching from classify
    workflow.add_conditional_edges(
        "classify",
        router_condition,
        {
            "research": "research",
            "knowledge": "knowledge",
            "coding": "coding",
            "assessment": "assessment",
            "tutor": "tutor",
        }
    )

    # Sequence: Research flows into Tutor to synthesize external sources
    workflow.add_edge("research", "tutor")

    # Terminal edges
    workflow.add_edge("tutor", END)
    workflow.add_edge("coding", END)
    workflow.add_edge("assessment", END)
    workflow.add_edge("knowledge", END)

    # In-memory checkpointer for stateful sessions
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)

# Global compiled orchestrator
orchestrator_app = build_orchestrator_graph()

async def run_orchestrator(
    user_id: str,
    session_id: str,
    message: str,
    learning_level: str = "intermediate",
    explanation_depth: str = "standard",
    learning_goal: str = None,
    require_search: bool = False
) -> AthenaState:
    """
    Runs the full multi-agent orchestration for a student message.
    """
    initial_state: AthenaState = {
        "user_id": user_id,
        "session_id": session_id,
        "current_request": message,
        "current_topic": "Computer Science",
        "learning_level": learning_level,
        "explanation_depth": explanation_depth,
        "learning_goal": learning_goal,
        "conversation_messages": [],
        "relevant_memory": {"require_search": require_search},
        "requested_agents": [],
        "active_agent": "Orchestrator Agent",
        "retrieved_documents": [],
        "web_sources": [],
        "research_findings": None,
        "tutor_output": None,
        "coding_output": None,
        "assessment_output": None,
        "final_response": "",
        "workflow_status": "in_progress",
        "tool_errors": [],
        "approval_status": None
    }

    config = {"configurable": {"thread_id": session_id}}
    final_state = await orchestrator_app.ainvoke(initial_state, config=config)
    final_state["workflow_status"] = "completed"
    return final_state
