# API Documentation — Athena AI/CS Study Assistant

The Athena backend provides versioned REST and Server-Sent Events (SSE) endpoints under `/api/v1`.
Interactive Swagger UI is also available at `http://localhost:8000/docs`.

---

## Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/chat` | Send a message and receive a synchronous multi-agent orchestrated response |
| `POST` | `/api/v1/chat/stream` | Send a message and receive an SSE stream of status chunks and tokens |
| `POST` | `/api/v1/chat/approval` | Submit approval/rejection for actions paused at human checkpoints |
| `GET` | `/api/v1/sessions` | List saved learning sessions for a student |
| `GET` | `/api/v1/sessions/{session_id}` | Retrieve message history and metadata for a session |
| `DELETE` | `/api/v1/sessions/{session_id}` | Delete or clear a learning session |
| `GET` | `/api/v1/documents` | List uploaded learning materials (UI Prototype) |
| `POST` | `/api/v1/documents/upload` | Validate and upload a document (UI Prototype) |
| `DELETE` | `/api/v1/documents/{document_id}` | Delete an uploaded document |
| `POST` | `/api/v1/documents/{document_id}/reindex` | Simulate reindexing for UI demonstration |
| `POST` | `/api/v1/quiz/generate` | Generate structured practice questions on a topic |
| `POST` | `/api/v1/quiz/submit` | Evaluate submitted answers, score, and diagnose knowledge gaps |
| `GET` | `/api/v1/learning/progress` | Get learner profile, study statistics, and topics to review |
| `POST` | `/api/v1/learning/preferences` | Update student preferences (level, depth, language) |
| `DELETE` | `/api/v1/learning/reset` | Clear all recorded student history (privacy control) |
| `GET` | `/api/v1/health` | System health check, active LLM, database, and MCP status |

---

## Detailed Endpoint Specifications

### 1. `POST /api/v1/chat`

**Request Body**:
```json
{
  "message": "Explain Binary Search Trees",
  "session_id": "session-1234",
  "user_id": "guest",
  "learning_level": "intermediate",
  "explanation_depth": "standard",
  "learning_goal": "Algorithms Mastery",
  "require_search": false
}
```

**Response Body (200 OK)**:
```json
{
  "session_id": "session-1234",
  "response": "Binary Search Trees (BST) organize items in sorted order...",
  "active_agent": "Tutor Agent",
  "agents_involved": ["Orchestrator Agent", "Tutor Agent"],
  "sources": [],
  "code_analysis": null,
  "approval_required": false,
  "approval_token": null
}
```

---

### 2. `POST /api/v1/chat/stream`

Streams Server-Sent Events with `text/event-stream`.

**Stream Chunk Format**:
```text
data: {"type": "status", "agent": "Orchestrator Agent", "content": "Analyzing query & active context..."}

data: {"type": "status", "agent": "Tutor Agent", "content": "Structuring standard explanation for intermediate level..."}

data: {"type": "token", "agent": "Tutor Agent", "content": "**Binary Search** is a "}

data: {"type": "sources", "data": [{"title": "Docs", "url": "https://..."}]}

data: {"type": "done", "agent": "Tutor Agent", "session_id": "session-1234"}
```

---

### 3. `POST /api/v1/quiz/generate`

**Request Body**:
```json
{
  "topic": "Transformer Attention Mechanisms",
  "learning_level": "intermediate",
  "count": 3
}
```

**Response Body (200 OK)**:
```json
{
  "quiz_id": "7b824ef7-bca9-482f-8dcf-3ff3d35aaef1",
  "topic": "Transformer Attention Mechanisms",
  "learning_level": "intermediate",
  "questions": [
    {
      "id": "q1",
      "question": "Why is the dot-product scaled by 1/sqrt(d_k)?",
      "type": "multiple_choice",
      "options": ["To prevent gradients from vanishing in softmax", "To speed up matrix multiplication"],
      "correct_answer": "To prevent gradients from vanishing in softmax",
      "explanation": "Large values of d_k push softmax into regions of vanishing gradients."
    }
  ]
}
```

---

### 4. `POST /api/v1/quiz/submit`

**Request Body**:
```json
{
  "quiz_id": "7b824ef7-bca9-482f-8dcf-3ff3d35aaef1",
  "topic": "Transformer Attention Mechanisms",
  "user_id": "guest",
  "answers": [
    {
      "question_id": "q1",
      "selected_answer": "To speed up matrix multiplication"
    }
  ]
}
```

**Response Body (200 OK)**:
```json
{
  "quiz_id": "7b824ef7-bca9-482f-8dcf-3ff3d35aaef1",
  "score": 0,
  "total": 1,
  "percentage": 0.0,
  "evaluations": [
    {
      "question_id": "q1",
      "question_text": "Why is the dot-product scaled by 1/sqrt(d_k)?",
      "selected_answer": "To speed up matrix multiplication",
      "correct_answer": "To prevent gradients from vanishing in softmax",
      "is_correct": false,
      "explanation": "Large values of d_k push softmax into regions of vanishing gradients."
    }
  ],
  "knowledge_gaps": ["Misconception on: Why is the dot-product scaled..."],
  "recommended_revision": ["Review core fundamentals of Transformer Attention Mechanisms"]
}
```
