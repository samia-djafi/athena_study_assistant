import React, { useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  HelpCircle,
  ArrowRight,
  RefreshCw,
  Sparkles,
  Award,
  BookOpen
} from 'lucide-react';
import { QuizQuestion, QuizSubmissionResponse, LearningLevel } from '../types';
import { generateQuiz, submitQuiz } from '../api';

export const QuizWorkspace: React.FC = () => {
  const [topic, setTopic] = useState('Binary Search Trees');
  const [level, setLevel] = useState<LearningLevel>('intermediate');
  const [questionCount, setQuestionCount] = useState<number>(5);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [quizData, setQuizData] = useState<{ quiz_id: string; topic: string; questions: QuizQuestion[] } | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<QuizSubmissionResponse | null>(null);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    try {
      setLoading(true);
      setResult(null);
      setSelectedAnswers({});
      const data = await generateQuiz(topic, level, questionCount);
      setQuizData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOption = (questionId: string, option: string) => {
    setSelectedAnswers((prev) => ({ ...prev, [questionId]: option }));
  };

  const handleSubmit = async () => {
    if (!quizData) return;
    try {
      setSubmitting(true);
      const answerPayload = Object.entries(selectedAnswers).map(([qid, ans]) => ({
        question_id: qid,
        selected_answer: ans
      }));
      const res = await submitQuiz(quizData.quiz_id, quizData.topic, 'guest', answerPayload);
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen bg-charcoal-950 overflow-y-auto">
      {/* Header */}
      <header className="p-6 border-b border-charcoal-800 bg-charcoal-900/60">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-charcoal-100 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-gold" />
              <span>Assessment & Practice Quizzes</span>
            </h1>
            <p className="text-xs text-charcoal-400 mt-1">
              Test conceptual understanding with structured questions, immediate scoring, and diagnostic feedback.
            </p>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto w-full p-6 space-y-6">
        {/* Quiz Configuration Panel */}
        <div className="p-5 rounded-xl bg-charcoal-900 border border-charcoal-800 flex flex-wrap items-end gap-4">
          <div className="flex-1 min-w-[240px]">
            <label className="block text-xs font-medium text-charcoal-300 mb-1.5">
              CS / AI Topic
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. Dynamic Programming, Transformers, Graph Search"
              className="w-full bg-charcoal-850 border border-charcoal-700 rounded-lg px-3 py-2 text-xs text-charcoal-100 focus:outline-none focus:border-gold/50"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-charcoal-300 mb-1.5">
              Difficulty Level
            </label>
            <div className="flex bg-charcoal-850 rounded-lg p-0.5 border border-charcoal-700">
              {(['beginner', 'intermediate', 'advanced'] as LearningLevel[]).map((lvl) => (
                <button
                  key={lvl}
                  onClick={() => setLevel(lvl)}
                  className={`text-xs px-3 py-1.5 rounded-md capitalize font-medium transition-all ${
                    level === lvl
                      ? 'bg-charcoal-700 text-gold-light'
                      : 'text-charcoal-400 hover:text-charcoal-200'
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-charcoal-300 mb-1.5">
              Number of Questions
            </label>
            <div className="flex bg-charcoal-850 rounded-lg p-0.5 border border-charcoal-700">
              {[5, 10, 15, 20].map((count) => (
                <button
                  key={count}
                  type="button"
                  onClick={() => setQuestionCount(count)}
                  className={`text-xs px-2.5 py-1.5 rounded-md font-medium transition-all ${
                    questionCount === count
                      ? 'bg-charcoal-700 text-gold-light'
                      : 'text-charcoal-400 hover:text-charcoal-200'
                  }`}
                >
                  {count}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading || !topic.trim()}
            className="px-4 py-2 rounded-lg bg-gold text-charcoal-950 font-medium text-xs hover:bg-gold-light transition-all shadow-sm flex items-center gap-1.5 disabled:opacity-50"
          >
            {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
            <span>Generate Practice Quiz</span>
          </button>
        </div>

        {/* Quiz Questions View */}
        {quizData && !result && (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs text-charcoal-400 pb-1">
              <span>Topic: <strong className="text-gold-light">{quizData.topic}</strong></span>
              <span>{quizData.questions.length} Questions</span>
            </div>

            {quizData.questions.map((q, idx) => (
              <div key={q.id} className="p-5 rounded-xl bg-charcoal-900 border border-charcoal-800 space-y-3">
                <div className="text-xs font-medium text-charcoal-200 leading-relaxed">
                  <span className="text-gold mr-2 font-mono">Q{idx + 1}.</span>
                  {q.question}
                </div>

                <div className="space-y-2 pt-1">
                  {q.options?.map((opt, optIdx) => (
                    <button
                      key={optIdx}
                      onClick={() => handleSelectOption(q.id, opt)}
                      className={`w-full text-left p-2.5 rounded-lg text-xs transition-colors border flex items-center gap-2.5 ${
                        selectedAnswers[q.id] === opt
                          ? 'bg-charcoal-800 border-gold/60 text-gold-light'
                          : 'bg-charcoal-850/60 border-charcoal-800 text-charcoal-300 hover:bg-charcoal-800'
                      }`}
                    >
                      <div className={`w-4 h-4 rounded-full border flex items-center justify-center text-[10px] font-mono ${
                        selectedAnswers[q.id] === opt
                          ? 'border-gold bg-gold/20 text-gold-light'
                          : 'border-charcoal-600 text-charcoal-500'
                      }`}>
                        {String.fromCharCode(65 + optIdx)}
                      </div>
                      <span>{opt}</span>
                    </button>
                  ))}
                </div>
              </div>
            ))}

            <div className="flex justify-end pt-2">
              <button
                onClick={handleSubmit}
                disabled={submitting || Object.keys(selectedAnswers).length === 0}
                className="px-5 py-2.5 rounded-lg bg-gold text-charcoal-950 font-medium text-xs hover:bg-gold-light transition-all shadow-sm flex items-center gap-1.5 disabled:opacity-50"
              >
                {submitting ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ArrowRight className="w-3.5 h-3.5" />}
                <span>Submit & View Diagnostic Feedback</span>
              </button>
            </div>
          </div>
        )}

        {/* Results & Detailed Review */}
        {result && (
          <div className="space-y-6">
            {/* Score Summary Card */}
            <div className="p-6 rounded-xl bg-charcoal-900 border border-gold/40 flex items-center justify-between">
              <div>
                <div className="text-xs uppercase font-mono text-gold tracking-wider mb-1">Assessment Complete</div>
                <h3 className="text-xl font-semibold text-charcoal-100">
                  Score: {result.score} / {result.total} ({result.percentage}%)
                </h3>
                <p className="text-xs text-charcoal-400 mt-1">
                  {result.percentage >= 80 ? 'Mastery demonstrated!' : 'Good effort! Review the explanations below.'}
                </p>
              </div>

              <button
                onClick={() => {
                  setResult(null);
                  setSelectedAnswers({});
                  handleGenerate();
                }}
                className="px-4 py-2 rounded-lg bg-charcoal-800 hover:bg-charcoal-700 text-gold-light text-xs font-medium border border-charcoal-700 transition-colors"
              >
                Try Another Set
              </button>
            </div>

            {/* Knowledge Gaps & Revision Recommendations */}
            {(result.knowledge_gaps.length > 0 || result.recommended_revision.length > 0) && (
              <div className="p-5 rounded-xl bg-charcoal-900/60 border border-charcoal-800 space-y-3">
                <h4 className="text-xs font-semibold text-gold-light uppercase tracking-wider flex items-center gap-1.5">
                  <BookOpen className="w-4 h-4 text-gold" />
                  <span>Personalized Revision Roadmap</span>
                </h4>
                {result.recommended_revision.map((rec, i) => (
                  <div key={i} className="text-xs text-charcoal-300 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-gold"></span>
                    <span>{rec}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Question Breakdown */}
            <div className="space-y-3">
              <h4 className="text-xs font-semibold text-charcoal-300 uppercase tracking-wider">
                Detailed Evaluation & Explanations
              </h4>

              {result.evaluations.map((ev, i) => (
                <div
                  key={i}
                  className={`p-5 rounded-xl bg-charcoal-900 border space-y-2.5 ${
                    ev.is_correct ? 'border-green-500/30' : 'border-red-500/30'
                  }`}
                >
                  <div className="flex items-start justify-between text-xs font-medium text-charcoal-200">
                    <div>
                      <span className="text-gold mr-2 font-mono">Q{i + 1}.</span>
                      {ev.question_text}
                    </div>
                    {ev.is_correct ? (
                      <span className="flex items-center gap-1 text-green-400 text-xs font-medium">
                        <CheckCircle2 className="w-4 h-4" /> Correct
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-red-400 text-xs font-medium">
                        <XCircle className="w-4 h-4" /> Incorrect
                      </span>
                    )}
                  </div>

                  <div className="text-xs text-charcoal-400 space-y-1">
                    <div>Your answer: <strong className={ev.is_correct ? 'text-green-400' : 'text-red-400'}>{ev.selected_answer || 'None'}</strong></div>
                    {!ev.is_correct && (
                      <div>Correct answer: <strong className="text-gold-light">{ev.correct_answer}</strong></div>
                    )}
                  </div>

                  <div className="p-3 rounded-lg bg-charcoal-850/80 border border-charcoal-800 text-xs text-charcoal-300 leading-relaxed">
                    <strong className="text-gold/90 block mb-0.5 font-medium">Pedagogical Explanation:</strong>
                    {ev.explanation}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
