export type LearningLevel = 'beginner' | 'intermediate' | 'advanced';
export type ExplanationDepth = 'short' | 'standard' | 'detailed';

export interface WebSource {
  title: string;
  url: string;
  snippet: string;
  publication_date?: string;
  source_domain?: string;
}

export interface CodeAnalysisResult {
  language: string;
  is_safe: boolean;
  static_summary: string;
  ast_valid: boolean;
  complexity?: string;
  suggested_fixes: string[];
  has_executed: boolean;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  agent?: string;
  sources?: WebSource[];
  code_analysis?: CodeAnalysisResult;
  isStreaming?: boolean;
}

export interface SessionItem {
  id: string;
  title: string;
  topic?: string;
  created_at: number;
  updated_at: number;
}

export interface QuizQuestion {
  id: string;
  question: string;
  type: string;
  options?: string[];
  correct_answer: string;
  explanation: string;
}

export interface QuizEvaluationItem {
  question_id: string;
  question_text: string;
  selected_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation: string;
}

export interface QuizSubmissionResponse {
  quiz_id: string;
  score: number;
  total: number;
  percentage: number;
  evaluations: QuizEvaluationItem[];
  knowledge_gaps: string[];
  recommended_revision: string[];
}

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  size_bytes: number;
  status: 'Uploaded' | 'Processing' | 'Ready' | 'Failed';
  uploaded_at: number;
  note: string;
}

export interface LearnerProfile {
  user_id: string;
  preferred_level: LearningLevel;
  preferred_depth: ExplanationDepth;
  preferred_language: string;
  recently_studied_topics: string[];
  learning_goals: string[];
  total_study_sessions: number;
  total_quizzes_taken: number;
  average_quiz_score: number;
  topics_to_review: string[];
}
