"""
Knowledge Agent (RAG UI Prototype) for Athena AI/CS Study Assistant.

SPECIFICATION REQUIREMENT:
RAG and Knowledge Base is a UI prototype only. This agent strictly refuses to invent
document content or hallucinate citations, and clearly explains that document-based
answering is not yet implemented on the backend.
"""
import logging
from app.agents.state import AthenaState

logger = logging.getLogger(__name__)

PROTOTYPE_NOTICE = (
    "### 📄 Document Knowledge Base Notice (UI Prototype)\n\n"
    "Document-based answering (RAG) is currently in **UI Prototype** phase on the Athena platform.\n\n"
    "- **Backend Status**: Document indexing, chunking, vector embeddings, and semantic retrieval are not connected.\n"
    "- **Integrity Policy**: Athena refuses to fabricate document content, simulate fake retrieval, or hallucinate citations.\n\n"
    "You can view the document management interface in the **Study Materials / Knowledge Base** tab. "
    "For conceptual questions, I can explain the topic directly using verified Computer Science principles or live web research."
)

async def run_knowledge_agent(state: AthenaState) -> AthenaState:
    """
    Executes the Knowledge Agent placeholder node.
    Refuses to hallucinate document citations and explicitly communicates the UI prototype status.
    """
    query = state.get("current_request", "")
    logger.info(f"Knowledge Agent invoked for query: '{query}'")

    state["active_agent"] = "Knowledge Agent"
    if "requested_agents" not in state:
        state["requested_agents"] = []
    if "Knowledge Agent" not in state["requested_agents"]:
        state["requested_agents"].append("Knowledge Agent")

    # Explicitly indicate that no documents were retrieved
    state["retrieved_documents"] = []
    state["final_response"] = PROTOTYPE_NOTICE

    return state
