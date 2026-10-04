# Athena - AI/CS Study Assistant

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![React 19](https://img.shields.io/badge/React-18%2F19-61dafb.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-blueviolet.svg)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Athena is an intelligent, adaptive, multi-agent educational assistant designed for **Computer Science** and **Artificial Intelligence** students and independent learners. Athena behaves as a personal academic study environment that teaches, researches, explains, evaluates, and supports learning through a controlled, stateful multi-agent workflow.

---

## Key Features

- **Adaptive Instruction**: Switch dynamically between **Beginner**, **Intermediate**, and **Advanced** learning levels, and **Short**, **Standard**, or **Detailed** explanation depths.
- **LangGraph Multi-Agent Orchestration**: Stateful central orchestrator with conditional routing across 5 specialized agents:
  - **Tutor Agent**: Personalized explanations, analogies, step-by-step algorithms, and KaTeX math formatting.
  - **Research Agent**: Academic web search with domain ranking, snippet sanitization, and grounded citations.
  - **Coding Agent**: Static AST inspection, Big-O complexity analysis, and safe debugging guidance (**never executes arbitrary user code on the host**).
  - **Assessment Agent**: Practice quiz generation, answer scoring, mistake explanations, and diagnostic knowledge gap detection.
  - **Knowledge Agent**: RAG UI prototype placeholder with transparent integrity notices.
- **Safe Extensible Tools**:
  - AST-based mathematical calculator (no `eval()` vulnerabilities).
  - DuckDuckGo / Tavily technical web search.
  - Model Context Protocol (MCP) client abstraction.
- **RAG & Study Materials Interface**: Full-fidelity UI prototype showing document cards, upload progress (`Uploaded` → `Processing` → `Ready`), and retrieval previews.
- **Persistent Memory & Analytics**: Multi-turn conversation checkpointing, token boundary management with automatic summarization, learner preferences, and study analytics.
- **Zero-Cloud Local Development**: Works out of the box with SQLite and deterministic fallback models without requiring cloud or API credentials.

---

## Technology Stack

### Frontend
- **Framework**: React 18 / 19 with TypeScript and Vite
- **Styling**: Tailwind CSS with custom academic dark palette (charcoal `#0d0e12` and muted gold `#c5a059`)
- **Icons**: Lucide React
- **Markdown & Math**: `react-markdown` with `remark-gfm` and syntax-highlighted code blocks with copy controls
- **Streaming**: Server-Sent Events (SSE) reader

### Backend
- **Framework**: Python 3.11+ / 3.14 with FastAPI
- **Validation**: Pydantic v2 & Pydantic Settings
- **Orchestration**: LangGraph and LangChain Core
- **LLM Providers**: Groq API (`ChatGroq`) with seamless offline deterministic fallback
- **Database**: Local SQLite via `aiosqlite` and SQLAlchemy (Supabase PostgreSQL migrations included)
- **Testing**: `pytest` and `pytest-asyncio`

---

## Project Structure

```text
Athena/
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph orchestrator & 5 specialized agents
│   │   ├── api/             # REST & SSE streaming routes (/chat, /quiz, etc.)
│   │   ├── database/        # SQLite engine & SQLAlchemy models
│   │   ├── memory/          # Session manager, summarizer & profile store
│   │   ├── middleware/      # Security, request timing & approval checkpoints
│   │   ├── models/          # Pydantic schemas and typed definitions
│   │   ├── multimodal/      # Image validation & audio transcription boundary
│   │   ├── tools/           # Search, calculator, code analyzer & MCP client
│   │   ├── config.py        # Settings & environment variables
│   │   └── main.py          # FastAPI application entry point
│   ├── tests/               # 17-point automated pytest test suite
│   ├── requirements.txt     # Python backend dependencies
│   └── .env.example         # Environment template
├── frontend/
│   ├── src/
│   │   ├── components/      # Chat, KnowledgeBase, Quiz, Dashboard, Sidebar, Settings
│   │   ├── api.ts           # REST & SSE streaming client
│   │   ├── types.ts         # TypeScript data models
│   │   ├── App.tsx          # Main view coordinator
│   │   └── main.tsx         # Application entry
│   ├── package.json         # Frontend dependencies
│   ├── tailwind.config.js   # Custom dark charcoal / gold theme
│   └── vite.config.ts       # Vite config with /api proxy
├── docs/                    # Technical architecture & design documentation
│   ├── architecture.md
│   ├── agent_design.md
│   ├── rag_pipeline.md
│   ├── database_schema.md
│   ├── api_documentation.md
│   └── evaluation.md
└── README.md
```

---

## Getting Started

### Prerequisites
- **Python**: 3.11, 3.12, 3.13, or 3.14 (64-bit)
- **Node.js**: v18+ (tested with v24.21.0) and npm

---

### Backend Setup

1. Open a terminal in `backend`:
   ```powershell
   cd d:\Athena\backend
   ```
2. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Copy environment variables:
   ```powershell
   cp .env.example .env
   ```

4. Run the automated test suite:
   ```powershell
   python -m pytest tests/ -v
   ```
5. Start the backend server:
   ```powershell
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   Backend will be available at `http://localhost:8000` (API documentation at `http://localhost:8000/docs`).

---

### Frontend Setup

1. Open a terminal in `frontend`:
   ```powershell
   cd d:\Athena\frontend
   ```
2. Install npm packages:
   ```powershell
   npm install
   ```
3. Build for production:
   ```powershell
   npm run build
   ```
4. Start the development server:
   ```powershell
   npm run dev
   ```
   Frontend will be available at `http://localhost:3000` (or `http://localhost:5173`).

---

## LLM Provider & Offline Fallback Configuration

Athena supports runtime model configuration via environment variables:

- **Groq API**:
  ```env
  GROQ_API_KEY="gsk_your_groq_api_key_here"
  DEFAULT_MODEL="llama-3.3-70b-versatile"
  ```
- **Zero-Cloud Offline Fallback**:
  If `GROQ_API_KEY` is left blank, Athena automatically activates its `DeterministicEducationalModel`. This generates structured, pedagogically accurate responses for Computer Science and AI topics without failing or calling external services.

---

## Model Context Protocol (MCP) Configuration

Athena includes an extensible MCP client registry (`app/tools/mcp_client.py`).
To configure an external MCP server:
```python
from app.tools.mcp_client import mcp_client, MCPServerConfig, MCPToolDefinition

# Register server
mcp_client.register_server(MCPServerConfig(
    server_id="my-custom-mcp",
    name="Custom Server",
    transport="stdio",
    trusted=True
))

# Register tool
mcp_client.register_tool(MCPToolDefinition(
    name="my_tool",
    description="Tool description",
    server_id="my-custom-mcp",
    requires_approval=True
))
```

---

## Database & Supabase Deployment

For local development, Athena creates and manages `athena.db` using SQLite and `aiosqlite`.
---

## RAG & Knowledge Base Status Disclosure

> **RAG UI prototype — backend not implemented.**
>
> In accordance with the project specification:
> - The Knowledge Base page is an interactive user interface prototype demonstrating document cards, file upload progress, and processing workflows.
> - Embedding models, text chunking, and vector databases (such as Qdrant) are not running on the backend.
> - If a student asks questions about uploaded documents in chat, the Knowledge Agent will explicitly state that document-based answering is not yet implemented rather than fabricating citations.

---

## Security Considerations

- **No Arbitrary Code Execution**: The Coding Agent performs strictly static AST analysis. Untrusted code is never executed inside the FastAPI process or on the host machine.
- **Input Sanitization**: Web search snippets are filtered for prompt injection attempts (`ignore previous instructions`, etc.).
- **Session Privacy**: Multi-tenant session checks enforce strict ownership boundaries. Students cannot access another user's sessions or documents.
- **Human-in-the-Loop**: Consequential actions (such as deleting all study data) require an explicit confirmation checkpoint.

---

## Documentation Index

- [docs/architecture.md](docs/architecture.md) — System topology, component boundaries, and Mermaid diagrams.
- [docs/agent_design.md](docs/agent_design.md) — Shared state schema, routing rules, and agent definitions.
- [docs/rag_pipeline.md](docs/rag_pipeline.md) — UI prototype documentation and future vector architecture roadmap.
- [docs/database_schema.md](docs/database_schema.md) — Database ERD, table definitions, and Supabase SQL migrations.
- [docs/api_documentation.md](docs/api_documentation.md) — REST and SSE streaming endpoints, request/response payloads.
- [docs/evaluation.md](docs/evaluation.md) — 17-point test matrix and QA validation report.

---

## Author

**Samia DJAFI**  
AI Engineering Student | UMMTO  
Thirduni Program Participant

This project was developed as part of my learning journey in Artificial Intelligence through the **Thirduni Program**, in collaboration with the U.S. Embassy in Algeria.

Built with curiosity, experimentation, and a focus on understanding how AI agents, tools, and conversational memory work together.

**DJAFI Samia** · 2026