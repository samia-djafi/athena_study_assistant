"""
Research Agent for Athena AI/CS Study Assistant.
Performs focused academic and technical web research, retrieves source metadata,
and delivers structured findings without hallucinated citations.
"""
import logging
from typing import Dict, Any, List
from app.agents.state import AthenaState
from app.tools.web_search import search_web
from app.models.schemas import WebSource

logger = logging.getLogger(__name__)

async def run_research_agent(state: AthenaState) -> AthenaState:
    """
    Executes the Research Agent node in the LangGraph workflow.
    """
    query = state.get("current_request", "")
    logger.info(f"Research Agent invoked for query: '{query}'")

    state["active_agent"] = "Research Agent"
    if "requested_agents" not in state:
        state["requested_agents"] = []
    if "Research Agent" not in state["requested_agents"]:
        state["requested_agents"].append("Research Agent")

    try:
        sources: List[WebSource] = await search_web(query, max_results=4)
        
        # Save sources into state
        state["web_sources"] = [s.model_dump() for s in sources]
        
        # Build structured research findings
        findings_lines = [f"### Research Findings for '{query}':"]
        for idx, src in enumerate(sources, 1):
            findings_lines.append(f"{idx}. **[{src.title}]({src.url})** (Domain: `{src.source_domain}`)")
            findings_lines.append(f"   - *Summary*: {src.snippet}")
            
        state["research_findings"] = "\n".join(findings_lines)
    except Exception as e:
        logger.error(f"Research Agent failed: {e}")
        state["tool_errors"] = state.get("tool_errors", []) + [f"Web search error: {str(e)}"]
        state["research_findings"] = "Unable to retrieve external live sources at this time."

    return state
