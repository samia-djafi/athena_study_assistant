"""
Assessment Agent for Athena AI/CS Study Assistant.
Generates structured quizzes, evaluates submissions, explains mistakes,
and pinpoints knowledge gaps without leaking answers beforehand.
"""
import json
import uuid
import logging
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import AthenaState
from app.agents.llm_factory import get_llm
from app.models.schemas import (
    QuizQuestion, QuizType, QuizGenerateResponse,
    QuizSubmissionRequest, QuizSubmissionResponse, QuizEvaluationItem,
    LearningLevel
)

logger = logging.getLogger(__name__)

ASSESSMENT_SYSTEM_PROMPT = """You are Athena's Assessment Agent, specialized in CS/AI learning evaluation.
Your goal is to test conceptual mastery and problem-solving without revealing answers before the student submits them.
Always output valid JSON when generating questions.
"""

def generate_default_questions_for_topic(topic: str, level: str, count: int = 5) -> List[QuizQuestion]:
    """Generates comprehensive questions across difficulty levels for any requested count (5, 10, 15, 20)."""
    t_lower = topic.lower()
    
    # Base question catalog
    pool = [
        QuizQuestion(
            question=f"What is the average-case time complexity of searching in a balanced structure for {topic}?",
            type=QuizType.MCQ,
            options=["O(1)", "O(log n)", "O(n)", "O(n log n)"],
            correct_answer="O(log n)",
            explanation=f"In balanced data structures associated with {topic}, binary/tree search halves the search space at each level, resulting in logarithmic O(log n) time."
        ),
        QuizQuestion(
            question=f"Which property is essential to guarantee correctness in algorithms designed for {topic}?",
            type=QuizType.MCQ,
            options=[
                "A well-defined base case or termination condition",
                "Using exclusively global variables",
                "Avoiding all recursive subproblem calls",
                "Executing in linear O(n) space regardless of problem size"
            ],
            correct_answer="A well-defined base case or termination condition",
            explanation=f"Without a verified termination invariant or base condition, iterative and recursive algorithms for {topic} risk infinite loops or stack overflow errors."
        ),
        QuizQuestion(
            question=f"What is the primary trade-off when optimizing space complexity in {topic}?",
            type=QuizType.MCQ,
            options=[
                "Trading memory space for increased computation time (or recomputation)",
                "Guaranteeing that all data structures become immutable",
                "Doubling the recursion depth",
                "Eliminating input parameter validation"
            ],
            correct_answer="Trading memory space for increased computation time (or recomputation)",
            explanation="The space-time trade-off in computer science often requires recomputing intermediate results if caching/memoization memory is reduced."
        ),
        QuizQuestion(
            question=f"What is the worst-case time complexity if an unbalanced or adversarial input is provided in {topic}?",
            type=QuizType.MCQ,
            options=["O(1)", "O(log n)", "O(n)", "O(n^2)"],
            correct_answer="O(n)" if "tree" not in t_lower else "O(n)",
            explanation=f"Without balancing invariants, search structures and partition algorithms can degenerate to linear O(n) height or O(n^2) nested iterations."
        ),
        QuizQuestion(
            question=f"In {topic}, which technique is typically employed to prevent redundant calculations of overlapping subproblems?",
            type=QuizType.MCQ,
            options=[
                "Memoization / Dynamic Programming lookup tables",
                "Brute-force depth-first re-evaluation",
                "Randomized restarts",
                "Bitwise left-shift operators"
            ],
            correct_answer="Memoization / Dynamic Programming lookup tables",
            explanation="Storing previously solved subproblem states in a cache or table converts exponential tree recursions into polynomial time."
        ),
        QuizQuestion(
            question=f"How does increasing problem size n asymptotically impact {topic} if its complexity is O(n log n)?",
            type=QuizType.MCQ,
            options=[
                "Grows strictly slower than quadratic O(n^2) but faster than linear O(n)",
                "Grows at a constant rate independent of n",
                "Grows exponentially O(2^n)",
                "Decreases asymptotically towards zero"
            ],
            correct_answer="Grows strictly slower than quadratic O(n^2) but faster than linear O(n)",
            explanation="Linearithmic O(n log n) scaling is standard for efficient divide-and-conquer methods, vastly outperforming quadratic methods as n scales."
        ),
        QuizQuestion(
            question=f"Which data structure is most efficient for retrieving minimum/maximum priority elements in {topic}?",
            type=QuizType.MCQ,
            options=["Binary Min/Max Heap", "Singly Linked List", "Unsorted Array", "Static Stack"],
            correct_answer="Binary Min/Max Heap",
            explanation="A binary heap supports O(1) peek of the extremum and O(log n) insertion and extraction."
        ),
        QuizQuestion(
            question=f"What is a critical consideration for maintaining cache locality in {topic}?",
            type=QuizType.MCQ,
            options=[
                "Sequential contiguous memory access (e.g. flat arrays)",
                "Scattered pointer-chasing across random heap memory",
                "Deep recursive function call chains",
                "Allocating each element as an isolated node"
            ],
            correct_answer="Sequential contiguous memory access (e.g. flat arrays)",
            explanation="Modern CPU architectures heavily reward spatial locality; contiguous array buffers minimize CPU cache misses."
        ),
        QuizQuestion(
            question=f"In {topic}, what does a recurrence relation T(n) = 2T(n/2) + O(n) solve to using the Master Theorem?",
            type=QuizType.MCQ,
            options=["O(n log n)", "O(n^2)", "O(n)", "O(log n)"],
            correct_answer="O(n log n)",
            explanation="Case 2 of the Master Theorem applies: log_b(a) = log_2(2) = 1, matching f(n) = O(n^1), yielding O(n log n)."
        ),
        QuizQuestion(
            question=f"What is the impact of recursion stack depth on space complexity in {topic}?",
            type=QuizType.MCQ,
            options=[
                "Requires O(h) call stack memory where h is maximum recursion depth",
                "Consumes zero memory if functions are void",
                "Always uses O(1) memory on modern compilers",
                "Causes memory leaks unless garbage collected"
            ],
            correct_answer="Requires O(h) call stack memory where h is maximum recursion depth",
            explanation="Each recursive activation frame allocates stack frames; deep trees require O(h) auxiliary memory proportional to the depth."
        ),
        QuizQuestion(
            question=f"When analyzing {topic}, what is an amortized time analysis?",
            type=QuizType.MCQ,
            options=[
                "Average time per operation evaluated over a worst-case sequence of operations",
                "The absolute best-case single-step runtime",
                "The hardware clock cycle duration",
                "The average time taken on random inputs"
            ],
            correct_answer="Average time per operation evaluated over a worst-case sequence of operations",
            explanation="Amortized analysis guarantees the average performance of each operation in the worst case (e.g., dynamic array resizing is O(1) amortized)."
        ),
        QuizQuestion(
            question=f"Which invariant is preserved throughout execution in {topic}?",
            type=QuizType.MCQ,
            options=[
                "Loop invariant or state consistency at every step",
                "All variables remaining positive integers",
                "No memory reallocation throughout runtime",
                "The system clock remaining synchronized"
            ],
            correct_answer="Loop invariant or state consistency at every step",
            explanation="Formal algorithmic verification relies on showing that an invariant holds before, during, and after each iteration/substep."
        ),
        QuizQuestion(
            question=f"In {topic}, what distinguishes Depth-First Search (DFS) from Breadth-First Search (BFS)?",
            type=QuizType.MCQ,
            options=[
                "DFS explores as deep as possible using a stack/recursion; BFS explores level-by-level using a queue",
                "DFS is only for binary trees; BFS is for general graphs",
                "DFS guarantees shortest paths on unweighted graphs; BFS does not",
                "DFS runs in O(V^2); BFS runs in O(V+E)"
            ],
            correct_answer="DFS explores as deep as possible using a stack/recursion; BFS explores level-by-level using a queue",
            explanation="BFS uses a FIFO queue finding shortest paths on unweighted graphs, while DFS uses a LIFO stack traversing deep branches."
        ),
        QuizQuestion(
            question=f"What is the worst-case scenario for hashing operations in {topic}?",
            type=QuizType.MCQ,
            options=[
                "All keys colliding into the exact same hash bucket, degrading lookup to O(n)",
                "Hash table growing larger than system RAM",
                "Key values containing negative numbers",
                "Strings of length greater than 64 characters"
            ],
            correct_answer="All keys colliding into the exact same hash bucket, degrading lookup to O(n)",
            explanation="If all items collide into a single chain or bucket, retrieval drops from average O(1) to worst-case O(n) linked list traversal."
        ),
        QuizQuestion(
            question=f"In {topic}, what role does a pivot element play in partitioning algorithms?",
            type=QuizType.MCQ,
            options=[
                "Separates elements into sub-arrays of items smaller and larger than the pivot",
                "Serves as the root of a binary tree",
                "Terminates the program execution",
                "Calculates the memory hash code"
            ],
            correct_answer="Separates elements into sub-arrays of items smaller and larger than the pivot",
            explanation="Partitioning rearranges an array around a pivot such that elements smaller than the pivot precede it, and larger elements follow it."
        ),
        QuizQuestion(
            question=f"What is the mathematical condition for an algorithm in {topic} to be considered greedy?",
            type=QuizType.MCQ,
            options=[
                "It makes the locally optimal choice at each step hoping to find a global optimum",
                "It explores every possible branch in parallel",
                "It solves all subproblems backward from the destination",
                "It uses exponential time O(2^n)"
            ],
            correct_answer="It makes the locally optimal choice at each step hoping to find a global optimum",
            explanation="Greedy algorithms make myopic, locally optimal choices without backtracking, correct only when the problem exhibits the greedy-choice property."
        ),
        QuizQuestion(
            question=f"In {topic}, what is the significance of the P vs NP problem?",
            type=QuizType.MCQ,
            options=[
                "Determines whether problems verifiable in polynomial time can also be solved in polynomial time",
                "Determines whether parallel computing is faster than serial computing",
                "Measures the maximum RAM capacity of 64-bit processors",
                "Measures the network throughput of cloud servers"
            ],
            correct_answer="Determines whether problems verifiable in polynomial time can also be solved in polynomial time",
            explanation="P vs NP asks whether every problem whose solution can be efficiently verified by a computer can also be efficiently solved by a computer."
        ),
        QuizQuestion(
            question=f"Why is tail-call optimization advantageous when implementing recursive functions in {topic}?",
            type=QuizType.MCQ,
            options=[
                "Reuses the current stack frame, preventing stack overflow and reducing memory to O(1)",
                "Speeds up floating point matrix multiplication",
                "Converts the code into a multi-threaded process",
                "Automatically encrypts input data"
            ],
            correct_answer="Reuses the current stack frame, preventing stack overflow and reducing memory to O(1)",
            explanation="In tail-recursive functions, the compiler replaces the call with a jump/loop, avoiding accumulating new activation frames."
        ),
        QuizQuestion(
            question=f"How does an adversarial worst-case input differ from an average-case input in {topic}?",
            type=QuizType.MCQ,
            options=[
                "Adversarial inputs exploit structural weaknesses to trigger maximal algorithmic steps",
                "Adversarial inputs are always larger in byte size",
                "Average-case inputs always run in O(1) time",
                "Adversarial inputs cannot be parsed by compilers"
            ],
            correct_answer="Adversarial inputs exploit structural weaknesses to trigger maximal algorithmic steps",
            explanation="Worst-case analysis models an adversary crafting inputs specifically designed to maximize running time (e.g., sorted input for naive quicksort)."
        ),
        QuizQuestion(
            question=f"What is the key takeaway when evaluating algorithmic efficiency in {topic}?",
            type=QuizType.MCQ,
            options=[
                "Asymptotic bounds (Big-O, Omega, Theta) dictate scalability as data scales towards infinity",
                "Writing shorter code lines always produces faster machine code",
                "Hardware frequency always overcomes algorithmic sub-optimality",
                "Code readability is inversely related to computational speed"
            ],
            correct_answer="Asymptotic bounds (Big-O, Omega, Theta) dictate scalability as data scales towards infinity",
            explanation="Asymptotic complexity dominates real-world performance as dataset sizes increase, far outweighing minor constant-factor micro-optimizations."
        )
    ]
    return pool[:min(count, len(pool))]

async def generate_quiz(topic: str, level: LearningLevel = LearningLevel.INTERMEDIATE, count: int = 5) -> QuizGenerateResponse:
    """Generates structured questions for a topic matching the requested count (5, 10, 15, 20)."""
    # 1. Attempt dynamic LLM generation for diverse questions
    llm = get_llm()
    prompt = (
        f"Generate exactly {count} distinct, high-quality multiple choice assessment questions for {topic} at {level.value} level.\n"
        "Return ONLY a valid JSON list of objects matching this exact schema:\n"
        "[\n"
        "  {\n"
        "    \"question\": \"Question text here\",\n"
        "    \"options\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"],\n"
        "    \"correct_answer\": \"Option A\",\n"
        "    \"explanation\": \"Pedagogical explanation of why this answer is correct.\"\n"
        "  }\n"
        "]\n"
        "Do not include any other markdown text, backticks, or preamble outside the JSON."
    )
    
    try:
        resp = await llm.ainvoke([
            SystemMessage(content="You are an expert Computer Science evaluator. You must return only valid JSON array."),
            HumanMessage(content=prompt)
        ])
        content = resp.content.strip()
        # Clean potential markdown wrapping
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            if content.endswith("```"):
                content = content.rsplit("```", 1)[0]
        content = content.strip()
        
        parsed = json.loads(content)
        if isinstance(parsed, list) and len(parsed) > 0:
            llm_questions = []
            for item in parsed[:count]:
                q_text = item.get("question", "")
                opts = item.get("options", [])
                ans = item.get("correct_answer", "")
                expl = item.get("explanation", "")
                if q_text and len(opts) >= 2:
                    llm_questions.append(QuizQuestion(
                        id=str(uuid.uuid4()),
                        question=q_text,
                        type=QuizType.MCQ,
                        options=opts,
                        correct_answer=ans,
                        explanation=expl
                    ))
            if len(llm_questions) < count:
                pool = generate_default_questions_for_topic(topic, level.value, count)
                existing = {q.question.lower() for q in llm_questions}
                for q in pool:
                    if len(llm_questions) >= count:
                        break
                    if q.question.lower() not in existing:
                        llm_questions.append(q)
            if len(llm_questions) > 0:
                return QuizGenerateResponse(
                    quiz_id=str(uuid.uuid4()),
                    topic=topic,
                    learning_level=level,
                    questions=llm_questions[:count]
                )
    except Exception as e:
        logger.info(f"LLM quiz generation fell back to verified question pool: {e}")

    # Fallback to rich question catalog for reliable question generation
    questions = generate_default_questions_for_topic(topic, level.value, count)
    return QuizGenerateResponse(
        quiz_id=str(uuid.uuid4()),
        topic=topic,
        learning_level=level,
        questions=questions
    )

def evaluate_quiz_submission(submission: QuizSubmissionRequest, original_questions: List[QuizQuestion]) -> QuizSubmissionResponse:
    """
    Evaluates user answers, computes score, explains mistakes, and extracts knowledge gaps.
    """
    q_map = {q.id: q for q in original_questions}
    evaluations: List[QuizEvaluationItem] = []
    correct_count = 0
    knowledge_gaps = []
    recommended_revision = []

    for item in submission.answers:
        q = q_map.get(item.question_id)
        if not q:
            continue
        
        is_corr = item.selected_answer.strip().lower() == q.correct_answer.strip().lower()
        if is_corr:
            correct_count += 1
        else:
            gap_summary = f"Misconception on: {q.question[:60]}..."
            knowledge_gaps.append(gap_summary)
            recommended_revision.append(f"Review core fundamentals of {submission.topic}")

        evaluations.append(QuizEvaluationItem(
            question_id=q.id,
            question_text=q.question,
            selected_answer=item.selected_answer,
            correct_answer=q.correct_answer,
            is_correct=is_corr,
            explanation=q.explanation
        ))

    total = len(original_questions) if original_questions else len(submission.answers)
    percentage = round((correct_count / total * 100), 1) if total > 0 else 0.0

    return QuizSubmissionResponse(
        quiz_id=submission.quiz_id,
        score=correct_count,
        total=total,
        percentage=percentage,
        evaluations=evaluations,
        knowledge_gaps=list(set(knowledge_gaps)),
        recommended_revision=list(set(recommended_revision))
    )

async def run_assessment_agent(state: AthenaState) -> AthenaState:
    """
    Executes the Assessment Agent in the LangGraph workflow.
    """
    query = state.get("current_request", "")
    topic = state.get("current_topic", "Computer Science")
    level_str = state.get("learning_level", "intermediate")
    
    logger.info(f"Assessment Agent invoked for topic: '{topic}'")
    state["active_agent"] = "Assessment Agent"
    if "requested_agents" not in state:
        state["requested_agents"] = []
    if "Assessment Agent" not in state["requested_agents"]:
        state["requested_agents"].append("Assessment Agent")

    quiz_res = await generate_quiz(topic, LearningLevel(level_str), count=3)
    state["assessment_output"] = quiz_res.model_dump()

    # Create user-facing quiz prompt (WITHOUT revealing answers)
    quiz_lines = [
        f"### 📝 Practice Quiz: {topic} ({level_str.capitalize()} Level)\n",
        "Test your understanding by reviewing these questions:\n"
    ]
    for idx, q in enumerate(quiz_res.questions, 1):
        quiz_lines.append(f"**Question {idx}:** {q.question}")
        if q.options:
            for opt in q.options:
                quiz_lines.append(f"- [ ] {opt}")
        quiz_lines.append("")

    quiz_lines.append("\n*Select your answers in the interactive Quiz workspace or reply with your choices to receive detailed feedback.*")
    
    state["final_response"] = "\n".join(quiz_lines)
    return state
