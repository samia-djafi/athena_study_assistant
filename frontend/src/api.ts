import {
  LearningLevel,
  ExplanationDepth,
  SessionItem,
  DocumentItem,
  LearnerProfile,
  QuizQuestion,
  QuizSubmissionResponse,
  WebSource
} from './types';

const BACKEND_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const API_BASE = BACKEND_URL ? `${BACKEND_URL}/api/v1` : '/api/v1';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function fetchSessions(userId: string = 'guest'): Promise<SessionItem[]> {
  const res = await fetch(`${API_BASE}/sessions?user_id=${encodeURIComponent(userId)}`);
  if (!res.ok) throw new Error('Failed to load sessions');
  return res.json();
}

export async function fetchSessionDetails(sessionId: string, userId: string = 'guest') {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}?user_id=${encodeURIComponent(userId)}`);
  if (!res.ok) throw new Error('Failed to load session details');
  return res.json();
}

export async function deleteSession(sessionId: string, userId: string = 'guest') {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}?user_id=${encodeURIComponent(userId)}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to clear session');
  return res.json();
}

export async function fetchDocuments(userId: string = 'guest'): Promise<DocumentItem[]> {
  const res = await fetch(`${API_BASE}/documents?user_id=${encodeURIComponent(userId)}`);
  if (!res.ok) throw new Error('Failed to load documents');
  return res.json();
}

export async function uploadDocument(file: File, userId: string = 'guest'): Promise<DocumentItem> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('user_id', userId);

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to upload document');
  }
  return res.json();
}

export async function deleteDocument(docId: string, userId: string = 'guest') {
  const res = await fetch(`${API_BASE}/documents/${docId}?user_id=${encodeURIComponent(userId)}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to delete document');
  return res.json();
}

export async function generateQuiz(topic: string, level: LearningLevel, count: number = 3): Promise<{ quiz_id: string; topic: string; questions: QuizQuestion[] }> {
  const res = await fetch(`${API_BASE}/quiz/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, learning_level: level, count }),
  });
  if (!res.ok) throw new Error('Failed to generate quiz');
  return res.json();
}

export async function submitQuiz(
  quizId: string,
  topic: string,
  userId: string,
  answers: { question_id: string; selected_answer: string }[]
): Promise<QuizSubmissionResponse> {
  const res = await fetch(`${API_BASE}/quiz/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      quiz_id: quizId,
      topic,
      user_id: userId,
      answers
    }),
  });
  if (!res.ok) throw new Error('Failed to submit quiz');
  return res.json();
}

export async function fetchProgress(userId: string = 'guest'): Promise<LearnerProfile> {
  const res = await fetch(`${API_BASE}/learning/progress?user_id=${encodeURIComponent(userId)}`);
  if (!res.ok) throw new Error('Failed to load learner progress');
  return res.json();
}

export async function updatePreferences(
  userId: string = 'guest',
  prefs: {
    preferred_level?: LearningLevel;
    preferred_depth?: ExplanationDepth;
    preferred_language?: string;
  }
): Promise<LearnerProfile> {
  const res = await fetch(`${API_BASE}/learning/preferences`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, ...prefs }),
  });
  if (!res.ok) throw new Error('Failed to update preferences');
  return res.json();
}

export async function resetLearningProgress(userId: string = 'guest') {
  const res = await fetch(`${API_BASE}/learning/reset?user_id=${encodeURIComponent(userId)}`, {
    method: 'DELETE'
  });
  return res.json();
}

export async function streamChatResponse(
  params: {
    message: string;
    sessionId: string;
    userId: string;
    level: LearningLevel;
    depth: ExplanationDepth;
    requireSearch?: boolean;
    imageData?: string;
  },
  callbacks: {
    onStatus: (agent: string, status: string) => void;
    onToken: (token: string, agent?: string) => void;
    onSources: (sources: WebSource[]) => void;
    onDone: () => void;
    onError: (err: string) => void;
  }
) {
  try {
    const res = await fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: params.message,
        session_id: params.sessionId,
        user_id: params.userId,
        learning_level: params.level,
        explanation_depth: params.depth,
        require_search: params.requireSearch,
        image_data: params.imageData
      }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error: ${res.status}`);
    }

    const reader = res.body?.getReader();
    if (!reader) throw new Error('ReadableStream not supported.');

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const raw = line.slice(6).trim();
          if (!raw) continue;
          try {
            const parsed = JSON.parse(raw);
            if (parsed.type === 'status') {
              callbacks.onStatus(parsed.agent || 'Athena', parsed.content);
            } else if (parsed.type === 'token') {
              callbacks.onToken(parsed.content, parsed.agent);
            } else if (parsed.type === 'sources') {
              callbacks.onSources(parsed.data || []);
            } else if (parsed.type === 'done') {
              callbacks.onDone();
            } else if (parsed.type === 'error') {
              callbacks.onError(parsed.content || 'Stream error occurred.');
            }
          } catch (e) {
            console.error('Error parsing SSE event:', e);
          }
        }
      }
    }
    callbacks.onDone();
  } catch (error: any) {
    callbacks.onError(error.message || 'Network stream error.');
  }
}
