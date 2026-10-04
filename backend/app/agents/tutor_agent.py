"""
Tutor Agent for Athena AI/CS Study Assistant.
Delivers adaptive, personalized Computer Science and AI instruction.
Supports Beginner, Intermediate, and Advanced levels with Short, Standard, and Detailed depths.
"""
import logging
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AthenaState
from app.agents.llm_factory import get_llm
from app.models.schemas import LearningLevel, ExplanationDepth

logger = logging.getLogger(__name__)

TUTOR_SYSTEM_PROMPT = """You are Athena's Tutor Agent, an expert pedagogue in Computer Science and Artificial Intelligence.
Your mission is to provide clear, technically accurate, and pedagogically sound explanations.

You MUST follow these rules:
1. Respect the student's selected learning level:
   - Beginner: Use approachable intuition, everyday analogies, avoid dense jargon without defining it first, and emphasize fundamentals.
   - Intermediate: Balance formal CS terminology, practical implementation details, and standard algorithmic complexity analysis.
   - Advanced: Focus on formal proofs, mathematical formulations, low-level architecture, hardware nuances, edge cases, and optimization trade-offs.

2. Respect the student's requested explanation depth:
   - Short: A concise formal definition and the essential takeaway (max 2-3 sentences).
   - Standard: A structured explanation, core mechanics, and a clear concrete code or conceptual example.
   - Detailed: In-depth exploration covering conceptual foundation, step-by-step logic, code examples, edge cases, time/space complexity, and limitations.

3. Formatting:
   - Use clean, standard ASCII Markdown:
     * NEVER use mathematical Unicode characters for Markdown markup: use standard ASCII pipe '|' (U+007C) for tables (do NOT use Unicode '∣' U+2223), ASCII '*' for bold/italics, and ASCII '-' for lists and dividers.
     * All tables MUST be valid standard GitHub Flavored Markdown tables with leading and trailing pipes on every row, and a header divider row with pipes and dashes, e.g.:
       | Operation | Time Complexity (Average) | Time Complexity (Worst) | Space Complexity |
       | --- | --- | --- | --- |
       | Search | $O(\log n)$ | $O(h)$ | $O(1)$ |
       Each table row MUST be on its own line. NEVER smash multiple rows onto a single line.
     * Always write Big-O complexity wrapped in dollar signs: `$O(\log n)$`, `$O(n)$`, `$O(h)$`, `$O(1)$`, `$\Theta(\log n)$`. NEVER write bare `O\log n` without dollar signs.
   - Format ALL mathematical symbols, variables, and equations using standard KaTeX LaTeX delimiters:
     * Inline math: Always enclose in single dollar signs, e.g. $p_{\theta}(\mathbf{y}\mid\mathbf{x})$ or $O(n \log n)$.
     * Display math: Always place on its own line enclosed in double dollar signs:
       $$
       \mathcal{L}(\theta) = \sum_{(\mathbf{x},\mathbf{y})\in\mathcal{D}} \log p_{\theta}(\mathbf{y}\mid\mathbf{x})
       $$
     * NEVER use bare brackets `[ ... ]` or parentheses `( ... )` for math formulas.
   - Separate fenced code blocks (e.g. ```python) and section headers with clean blank lines.
   - Avoid conversational fluff or repetitive apologies. Go directly to the structured explanation.
"""

async def run_tutor_agent(state: AthenaState) -> AthenaState:
    """
    Executes the Tutor Agent node in the LangGraph workflow.
    """
    query = state.get("current_request", "")
    level = state.get("learning_level", LearningLevel.INTERMEDIATE.value)
    depth = state.get("explanation_depth", ExplanationDepth.STANDARD.value)
    topic = state.get("current_topic", "Computer Science")
    research_findings = state.get("research_findings")
    coding_output = state.get("coding_output")
    
    logger.info(f"Tutor Agent invoked: topic='{topic}', level='{level}', depth='{depth}'")

    system_instruction = (
        f"{TUTOR_SYSTEM_PROMPT}\n\n"
        f"Active Student Profile:\n"
        f"- Learning Level: {level.upper()}\n"
        f"- Explanation Depth: {depth.upper()}\n"
        f"- Current Topic: {topic}\n"
    )

    context_additions = []
    if research_findings:
        context_additions.append(f"External Research Findings to incorporate:\n{research_findings}")
    if coding_output:
        context_additions.append(f"Static Code Analysis findings:\n{coding_output.get('static_summary', '')}")

    user_prompt = query
    if context_additions:
        user_prompt += "\n\n" + "\n\n".join(context_additions)

    llm = get_llm()
    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=user_prompt)
    ]

    try:
        response = await llm.ainvoke(messages)
        tutor_response_text = response.content
    except Exception as e:
        logger.error(f"Error calling LLM in Tutor Agent: {e}")
        # Deterministic fallback response if LLM invocation fails
        if depth == ExplanationDepth.SHORT.value:
            tutor_response_text = f"**{topic}**: Core CS/AI concept operating under {level} parameters."
        else:
            tutor_response_text = (
                f"### {topic}\n\n"
                f"Explanation tailored for **{level}** learners at **{depth}** depth.\n"
                f"- **Core Concept**: Fundamental computational method.\n"
                f"- **Summary**: Focus on algorithm behavior and time complexity."
            )

    state["tutor_output"] = tutor_response_text
    state["active_agent"] = "Tutor Agent"
    
    # If this is the concluding agent in the sequence, set final_response
    if not state.get("final_response"):
        state["final_response"] = tutor_response_text

    return state
