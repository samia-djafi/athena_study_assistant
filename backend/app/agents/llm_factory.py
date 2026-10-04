"""
LLM provider abstraction and fallback system for Athena.
Supports Groq API when configured, and provides an offline deterministic mock fallback for local testing.
"""
import os
import logging
from typing import Any, List, Optional
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration
from app.config import settings

logger = logging.getLogger(__name__)

class DeterministicEducationalModel(BaseChatModel):
    """
    Offline educational LLM for Athena.
    Ensures that local development, automated testing, and mock-free testing work seamlessly
    without needing external cloud credentials.
    """
    model_name: str = "athena-educational-fallback"

    @property
    def _llm_type(self) -> str:
        return "athena_educational_fallback"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Any = None,
        **kwargs: Any
    ) -> ChatResult:
        last_message = messages[-1].content if messages else ""
        system_content = next((m.content for m in messages if isinstance(m, SystemMessage)), "")
        system_content_lower = system_content.lower()
        # Check exact profile line: "- explanation depth: <depth>"
        is_short = "- explanation depth: short" in system_content_lower or "depth: short" in system_content_lower
        is_detailed = "- explanation depth: detailed" in system_content_lower or "depth: detailed" in system_content_lower
        is_beginner = "- learning level: beginner" in system_content_lower
        is_advanced = "- learning level: advanced" in system_content_lower
        
        q_lower = last_message.lower()

        if "binary search" in q_lower or "bst" in q_lower:
            if is_short:
                text = "**Binary Search** is an efficient divide-and-conquer algorithm that finds the position of a target value within a sorted array in \\(O(\\log n)\\) time by repeatedly halving the search interval."
            elif is_detailed:
                text = (
                    "### Deep Dive: Binary Search Algorithm\n\n"
                    "**1. Core Principle**\n"
                    "Binary Search operates on a sorted sequence by comparing the search target with the middle element. "
                    "If the target matches the middle element, its position is returned. If the target is smaller, the search "
                    "continues in the left subarray; otherwise, in the right subarray.\n\n"
                    "**2. Mathematical Complexity**\n"
                    "- **Recurrence Relation**: \\(T(n) = T(n/2) + O(1)\\)\n"
                    "- **Time Complexity**: \\(O(\\log n)\\) in the worst and average cases, \\(O(1)\\) best case.\n"
                    "- **Space Complexity**: \\(O(1)\\) iterative, \\(O(\\log n)\\) recursive call stack.\n\n"
                    "**3. Implementation Nuance (Preventing Integer Overflow)**\n"
                    "In languages like C++ or Java, computing `mid = (low + high) / 2` can cause integer overflow when `low + high > 2^{31}-1`. "
                    "The standard industry pattern is `mid = low + (high - low) // 2`.\n\n"
                    "**4. Example in Python**\n"
                    "```python\n"
                    "def binary_search(arr: list[int], target: int) -> int:\n"
                    "    low, high = 0, len(arr) - 1\n"
                    "    while low <= high:\n"
                    "        mid = low + (high - low) // 2\n"
                    "        if arr[mid] == target:\n"
                    "            return mid\n"
                    "        elif arr[mid] < target:\n"
                    "            low = mid + 1\n"
                    "        else:\n"
                    "            high = mid - 1\n"
                    "    return -1\n"
                    "```"
                )
            else:
                text = (
                    "**Binary Search** is a search algorithm for sorted arrays.\n\n"
                    "- **Mechanism**: It compares the target with the median item. If unequal, the half in which the target cannot lie is eliminated.\n"
                    "- **Complexity**: \\(O(\\log n)\\) time and \\(O(1)\\) space.\n\n"
                    "**Python Example:**\n"
                    "```python\n"
                    "def binary_search(arr, target):\n"
                    "    low, high = 0, len(arr) - 1\n"
                    "    while low <= high:\n"
                    "        mid = (low + high) // 2\n"
                    "        if arr[mid] == target:\n"
                    "            return mid\n"
                    "        elif arr[mid] < target:\n"
                    "            low = mid + 1\n"
                    "        else:\n"
                    "            high = mid - 1\n"
                    "    return -1\n"
                    "```"
                )
        elif "attention" in q_lower or "transformer" in q_lower:
            text = (
                "### Transformer Scaled Dot-Product Attention\n\n"
                "Self-attention allows tokens to dynamically compute weights over all tokens in the sequence.\n\n"
                "\\[\n"
                "\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V\n"
                "\\]\n\n"
                "- \\(Q\\) (Queries): Representations of what token wants to find.\n"
                "- \\(K\\) (Keys): Representations of what tokens offer.\n"
                "- \\(V\\) (Values): The actual information content to retrieve.\n"
                "- \\(\\sqrt{d_k}\\): Scaling factor preventing the dot products from growing excessively large."
            )
        else:
            if is_short:
                text = f"**{last_message.strip()}**: Essential CS concept. Designed to solve algorithmic and computational problems efficiently."
            else:
                text = (
                    f"### Understanding {last_message.strip()}\n\n"
                    f"In Computer Science and AI, this concept represents a fundamental building block. "
                    f"It balances computational time, memory constraints, and implementation clarity.\n\n"
                    f"- **Core Idea**: Structured problem decomposition.\n"
                    f"- **Best Practice**: Verify boundary cases and algorithmic complexity.\n"
                    f"- **Next Steps**: Practice implementing test cases to verify edge behaviors."
                )

        generation = ChatGeneration(message=AIMessage(content=text))
        return ChatResult(generations=[generation])

def get_llm():
    """
    Returns the configured chat model.
    Uses ChatGroq if GROQ_API_KEY is present in settings or environment;
    otherwise falls back to DeterministicEducationalModel.
    """
    api_key = settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY")
    if api_key:
        try:
            from langchain_groq import ChatGroq
            return ChatGroq(
                groq_api_key=api_key,
                model_name=settings.DEFAULT_MODEL,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS
            )
        except Exception as e:
            logger.warning(f"Failed to initialize ChatGroq: {e}. Falling back to educational model.")
            
    return DeterministicEducationalModel()
