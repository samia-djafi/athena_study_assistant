import React from 'react';
import {
  MessageSquare,
  BookOpen,
  CheckCircle2,
  BarChart3,
  Settings,
  Plus,
  Trash2,
  Sparkles,
  GraduationCap,
  X
} from 'lucide-react';
import { SessionItem, LearnerProfile } from '../types';

interface SidebarProps {
  currentTab: 'chat' | 'knowledge' | 'quiz' | 'dashboard';
  setCurrentTab: (tab: 'chat' | 'knowledge' | 'quiz' | 'dashboard') => void;
  sessions: SessionItem[];
  activeSessionId: string;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string) => void;
  onOpenSettings: () => void;
  learnerProfile?: LearnerProfile;
  isOpenMobile?: boolean;
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  setCurrentTab,
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  onOpenSettings,
  learnerProfile,
  isOpenMobile = false,
  onCloseMobile
}) => {
  return (
    <aside
      className={`fixed inset-y-0 left-0 z-50 w-72 bg-charcoal-900 border-r border-charcoal-700/60 flex flex-col h-screen select-none transition-transform duration-300 ease-in-out md:static md:w-64 md:translate-x-0 ${
        isOpenMobile ? 'translate-x-0 shadow-2xl' : '-translate-x-full'
      }`}
    >
      {/* Brand Header */}
      <div className="p-4 border-b border-charcoal-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gold/15 border border-gold/40 flex items-center justify-center text-gold">
            <GraduationCap className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-semibold text-charcoal-100 text-sm tracking-wide flex items-center gap-1.5">
              Athena
              <span className="text-[10px] font-mono px-1 py-0.2 rounded bg-gold/20 text-gold-light border border-gold/30">AI/CS</span>
            </h1>
            <p className="text-[11px] text-charcoal-400">Study Assistant</p>
          </div>
        </div>

        {onCloseMobile && (
          <button
            onClick={onCloseMobile}
            className="md:hidden p-1.5 text-charcoal-400 hover:text-charcoal-100 rounded-lg hover:bg-charcoal-800 transition-colors"
            title="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Main Navigation */}
      <nav className="p-3 space-y-1">
        <button
          onClick={() => {
            setCurrentTab('chat');
            onCloseMobile?.();
          }}
          className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
            currentTab === 'chat'
              ? 'bg-charcoal-800 text-gold-light border border-gold/20'
              : 'text-charcoal-300 hover:bg-charcoal-850 hover:text-charcoal-100'
          }`}
        >
          <MessageSquare className="w-4 h-4 text-gold/80" />
          <span>Chat Workspace</span>
        </button>

        <button
          onClick={() => {
            setCurrentTab('knowledge');
            onCloseMobile?.();
          }}
          className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
            currentTab === 'knowledge'
              ? 'bg-charcoal-800 text-gold-light border border-gold/20'
              : 'text-charcoal-300 hover:bg-charcoal-850 hover:text-charcoal-100'
          }`}
        >
          <BookOpen className="w-4 h-4 text-gold/80" />
          <span>Study Materials</span>
          <span className="ml-auto text-[10px] bg-charcoal-700 text-charcoal-400 px-1 rounded font-mono">Demo</span>
        </button>

        <button
          onClick={() => {
            setCurrentTab('quiz');
            onCloseMobile?.();
          }}
          className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
            currentTab === 'quiz'
              ? 'bg-charcoal-800 text-gold-light border border-gold/20'
              : 'text-charcoal-300 hover:bg-charcoal-850 hover:text-charcoal-100'
          }`}
        >
          <CheckCircle2 className="w-4 h-4 text-gold/80" />
          <span>Quizzes & Practice</span>
        </button>

        <button
          onClick={() => {
            setCurrentTab('dashboard');
            onCloseMobile?.();
          }}
          className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
            currentTab === 'dashboard'
              ? 'bg-charcoal-800 text-gold-light border border-gold/20'
              : 'text-charcoal-300 hover:bg-charcoal-850 hover:text-charcoal-100'
          }`}
        >
          <BarChart3 className="w-4 h-4 text-gold/80" />
          <span>Learning Dashboard</span>
        </button>
      </nav>

      {/* New Session Button */}
      <div className="px-3 pt-2">
        <button
          onClick={() => {
            onNewSession();
            onCloseMobile?.();
          }}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-md text-xs font-medium bg-gold/15 text-gold-light border border-gold/30 hover:bg-gold/25 transition-all shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>New Conversation</span>
        </button>
      </div>

      {/* Recent Sessions List */}
      <div className="flex-1 overflow-y-auto px-3 py-2">
        <div className="text-[11px] font-medium text-charcoal-500 uppercase tracking-wider px-2 py-1 mb-1">
          Recent Sessions
        </div>
        <div className="space-y-0.5">
          {sessions.length === 0 ? (
            <p className="text-xs text-charcoal-500 px-2 py-3 italic">No recent sessions.</p>
          ) : (
            sessions.map((sess) => (
              <div
                key={sess.id}
                className={`group flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs transition-colors cursor-pointer ${
                  activeSessionId === sess.id
                    ? 'bg-charcoal-800 text-charcoal-100 border border-charcoal-700'
                    : 'text-charcoal-400 hover:bg-charcoal-850 hover:text-charcoal-200'
                }`}
                onClick={() => {
                  setCurrentTab('chat');
                  onSelectSession(sess.id);
                  onCloseMobile?.();
                }}
              >
                <span className="truncate pr-2 font-normal">{sess.title || 'CS Session'}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(sess.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-400 transition-opacity"
                  title="Clear session"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Footer & User Profile */}
      <div className="p-3 border-t border-charcoal-800/80 bg-charcoal-950/40">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-charcoal-800 border border-gold/30 flex items-center justify-center text-xs text-gold-light font-medium">
              AL
            </div>
            <div>
              <p className="text-xs font-medium text-charcoal-200">Athena Learner</p>
              <p className="text-[10px] text-charcoal-400 capitalize">
                {learnerProfile?.preferred_level || 'Intermediate'} • {learnerProfile?.preferred_depth || 'Standard'}
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              onOpenSettings();
              onCloseMobile?.();
            }}
            className="p-1.5 rounded-md text-charcoal-400 hover:text-charcoal-100 hover:bg-charcoal-800 transition-colors"
            title="Settings"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};
