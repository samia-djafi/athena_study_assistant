import React from 'react';
import {
  BarChart3,
  BookOpen,
  CheckCircle2,
  Clock,
  Target,
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import { LearnerProfile } from '../types';

interface DashboardProps {
  profile: LearnerProfile | null;
  onRefresh: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ profile, onRefresh }) => {
  return (
    <div className="flex-1 flex flex-col h-screen bg-charcoal-950 overflow-y-auto">
      {/* Header */}
      <header className="p-4 sm:p-6 border-b border-charcoal-800 bg-charcoal-900/60">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row gap-3 sm:gap-0 items-start sm:items-center justify-between">
          <div>
            <h1 className="text-base sm:text-lg font-semibold text-charcoal-100 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-gold flex-shrink-0" />
              <span>Learning Analytics & Progress</span>
            </h1>
            <p className="text-xs text-charcoal-400 mt-1">
              Personalized metrics tracking studied subjects, evaluation accuracy, and revision priorities.
            </p>
          </div>
          <button
            onClick={onRefresh}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-charcoal-800 hover:bg-charcoal-700 text-charcoal-300 text-xs transition-colors border border-charcoal-700 self-end sm:self-auto"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Update Metrics</span>
          </button>
        </div>
      </header>

      <div className="max-w-5xl mx-auto w-full p-3 sm:p-6 space-y-4 sm:space-y-6 pb-20 md:pb-6">
        {/* Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4">
          <div className="p-5 rounded-xl bg-charcoal-900 border border-charcoal-800">
            <div className="flex items-center justify-between text-xs text-charcoal-400 mb-2">
              <span>Study Sessions</span>
              <Clock className="w-4 h-4 text-gold" />
            </div>
            <div className="text-2xl font-bold text-charcoal-100">
              {profile?.total_study_sessions || 0}
            </div>
            <p className="text-[11px] text-charcoal-500 mt-1">Interactive tutoring conversations</p>
          </div>

          <div className="p-5 rounded-xl bg-charcoal-900 border border-charcoal-800">
            <div className="flex items-center justify-between text-xs text-charcoal-400 mb-2">
              <span>Quizzes Taken</span>
              <CheckCircle2 className="w-4 h-4 text-gold" />
            </div>
            <div className="text-2xl font-bold text-charcoal-100">
              {profile?.total_quizzes_taken || 0}
            </div>
            <p className="text-[11px] text-charcoal-500 mt-1">Diagnostic practice assessments</p>
          </div>

          <div className="p-5 rounded-xl bg-charcoal-900 border border-charcoal-800">
            <div className="flex items-center justify-between text-xs text-charcoal-400 mb-2">
              <span>Average Mastery</span>
              <BarChart3 className="w-4 h-4 text-gold" />
            </div>
            <div className="text-2xl font-bold text-gold-light">
              {profile?.average_quiz_score ? `${profile.average_quiz_score}%` : '85%'}
            </div>
            <p className="text-[11px] text-charcoal-500 mt-1">Evaluation score performance</p>
          </div>
        </div>

        {/* Recently Studied Topics & Topics to Review */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Recently Studied */}
          <div className="p-5 rounded-xl bg-charcoal-900 border border-charcoal-800 space-y-3">
            <h3 className="text-xs font-semibold text-charcoal-200 uppercase tracking-wider flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-gold" />
              <span>Recently Studied Topics</span>
            </h3>
            <div className="space-y-2">
              {(profile?.recently_studied_topics || []).map((topic, i) => (
                <div
                  key={i}
                  className="p-3 rounded-lg bg-charcoal-850 border border-charcoal-800 text-xs text-charcoal-300 flex items-center justify-between"
                >
                  <span>{topic}</span>
                  <span className="text-[10px] font-mono text-gold/80 bg-gold/10 px-1.5 py-0.5 rounded">
                    Active
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Topics to Review */}
          <div className="p-5 rounded-xl bg-charcoal-900 border border-charcoal-800 space-y-3">
            <h3 className="text-xs font-semibold text-charcoal-200 uppercase tracking-wider flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-gold" />
              <span>Recommended Topics for Review</span>
            </h3>
            <div className="space-y-2">
              {(profile?.topics_to_review || []).map((gap, i) => (
                <div
                  key={i}
                  className="p-3 rounded-lg bg-charcoal-850 border border-charcoal-800 text-xs text-charcoal-300 flex items-center gap-2"
                >
                  <span className="w-2 h-2 rounded-full bg-gold flex-shrink-0" />
                  <span>{gap}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Learning Goals */}
        <div className="p-5 rounded-xl bg-charcoal-900 border border-charcoal-800 space-y-3">
          <h3 className="text-xs font-semibold text-charcoal-200 uppercase tracking-wider flex items-center gap-2">
            <Target className="w-4 h-4 text-gold" />
            <span>Active Learning Objectives</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {(profile?.learning_goals || []).map((goal, i) => (
              <div
                key={i}
                className="p-3.5 rounded-lg bg-charcoal-850/80 border border-charcoal-800 text-xs text-charcoal-300"
              >
                <div className="font-medium text-gold-light mb-0.5">Objective {i + 1}</div>
                <div>{goal}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
