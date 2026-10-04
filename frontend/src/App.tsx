import React, { useState, useEffect } from 'react';
import {
  Menu,
  MessageSquare,
  BookOpen,
  CheckCircle2,
  BarChart3,
  Plus,
  Settings,
  GraduationCap
} from 'lucide-react';
import { Sidebar } from './components/Sidebar';
import { ChatWorkspace } from './components/ChatWorkspace';
import { KnowledgeBase } from './components/KnowledgeBase';
import { QuizWorkspace } from './components/QuizWorkspace';
import { Dashboard } from './components/Dashboard';
import { SettingsModal } from './components/SettingsModal';
import {
  Message,
  SessionItem,
  DocumentItem,
  LearnerProfile,
  LearningLevel,
  ExplanationDepth
} from './types';
import {
  fetchSessions,
  fetchSessionDetails,
  deleteSession,
  fetchDocuments,
  fetchProgress
} from './api';

export function App() {
  const [currentTab, setCurrentTab] = useState<'chat' | 'knowledge' | 'quiz' | 'dashboard'>('chat');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>(() => `session-${Date.now()}`);
  const [messages, setMessages] = useState<Message[]>([]);
  const [level, setLevel] = useState<LearningLevel>('intermediate');
  const [depth, setDepth] = useState<ExplanationDepth>('standard');
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [profile, setProfile] = useState<LearnerProfile | null>(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Load initial data
  useEffect(() => {
    loadSessions();
    loadDocuments();
    loadProfile();
  }, []);

  const loadSessions = async () => {
    try {
      const data = await fetchSessions('guest');
      setSessions(data);
      if (data.length > 0 && !activeSessionId) {
        setActiveSessionId(data[0].id);
        loadSessionMessages(data[0].id);
      }
    } catch (err) {
      console.error('Error fetching sessions:', err);
    }
  };

  const loadSessionMessages = async (id: string) => {
    try {
      const details = await fetchSessionDetails(id, 'guest');
      if (details?.messages) {
        setMessages(
          details.messages.map((m: any) => ({
            id: m.id,
            role: m.role,
            content: m.content,
            timestamp: m.timestamp * 1000,
            agent: m.metadata?.agent
          }))
        );
      } else {
        setMessages([]);
      }
    } catch (err) {
      console.error('Error loading session messages:', err);
      setMessages([]);
    }
  };

  const loadDocuments = async () => {
    try {
      const data = await fetchDocuments('guest');
      setDocuments(data);
    } catch (err) {
      console.error('Error fetching documents:', err);
    }
  };

  const loadProfile = async () => {
    try {
      const data = await fetchProgress('guest');
      setProfile(data);
      if (data.preferred_level) setLevel(data.preferred_level);
      if (data.preferred_depth) setDepth(data.preferred_depth);
    } catch (err) {
      console.error('Error fetching learner profile:', err);
    }
  };

  const handleSelectSession = (id: string) => {
    setActiveSessionId(id);
    loadSessionMessages(id);
  };

  const handleNewSession = () => {
    const newId = `session-${Date.now()}`;
    setActiveSessionId(newId);
    setMessages([]);
    setCurrentTab('chat');
  };

  const handleDeleteSession = async (id: string) => {
    try {
      await deleteSession(id, 'guest');
      const updated = sessions.filter((s) => s.id !== id);
      setSessions(updated);
      if (activeSessionId === id) {
        handleNewSession();
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex h-screen bg-charcoal-950 font-sans text-charcoal-100 overflow-hidden relative">
      {/* Mobile Backdrop for Sidebar Drawer */}
      {isMobileMenuOpen && (
        <div
          onClick={() => setIsMobileMenuOpen(false)}
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 md:hidden transition-opacity"
        />
      )}

      {/* Sidebar Drawer */}
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
        onDeleteSession={handleDeleteSession}
        onOpenSettings={() => setIsSettingsOpen(true)}
        learnerProfile={profile || undefined}
        isOpenMobile={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
      />

      {/* Main Container */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Mobile Top Header (Visible only on < md) */}
        <header className="md:hidden h-14 border-b border-charcoal-800 bg-charcoal-900/90 px-3.5 flex items-center justify-between flex-shrink-0 z-30">
          <div className="flex items-center gap-2.5">
            <button
              onClick={() => setIsMobileMenuOpen(true)}
              className="p-1.5 text-charcoal-300 hover:text-gold-light rounded-lg hover:bg-charcoal-800 transition-colors"
              title="Open menu"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-gold/15 border border-gold/40 flex items-center justify-center text-gold">
                <GraduationCap className="w-4 h-4" />
              </div>
              <span className="font-semibold text-sm text-charcoal-100 tracking-tight">Athena</span>
              <span className="text-[10px] font-mono px-1 py-0.2 rounded bg-gold/20 text-gold-light border border-gold/30">AI/CS</span>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={handleNewSession}
              className="p-1.5 text-charcoal-300 hover:text-gold-light rounded-lg hover:bg-charcoal-800 transition-colors"
              title="New Chat"
            >
              <Plus className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsSettingsOpen(true)}
              className="p-1.5 text-charcoal-300 hover:text-gold-light rounded-lg hover:bg-charcoal-800 transition-colors"
              title="Settings"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </header>

        {/* View Component */}
        <main className="flex-1 flex overflow-hidden relative">
          {currentTab === 'chat' && (
            <ChatWorkspace
              sessionId={activeSessionId}
              messages={messages}
              setMessages={setMessages}
              level={level}
              setLevel={setLevel}
              depth={depth}
              setDepth={setDepth}
              onSessionUpdated={() => {
                loadSessions();
                loadProfile();
              }}
            />
          )}

          {currentTab === 'knowledge' && (
            <KnowledgeBase
              documents={documents}
              onRefreshDocs={loadDocuments}
            />
          )}

          {currentTab === 'quiz' && (
            <QuizWorkspace />
          )}

          {currentTab === 'dashboard' && (
            <Dashboard
              profile={profile}
              onRefresh={loadProfile}
            />
          )}
        </main>

        {/* Mobile Bottom Navigation Bar (Visible only on < md) */}
        <nav className="md:hidden h-14 border-t border-charcoal-800 bg-charcoal-900/95 px-2 flex items-center justify-around flex-shrink-0 z-30">
          <button
            onClick={() => setCurrentTab('chat')}
            className={`flex flex-col items-center justify-center py-1 px-3 rounded-lg text-[10px] font-medium transition-colors ${
              currentTab === 'chat'
                ? 'text-gold-light'
                : 'text-charcoal-400 hover:text-charcoal-200'
            }`}
          >
            <MessageSquare className={`w-4 h-4 mb-0.5 ${currentTab === 'chat' ? 'text-gold' : 'text-charcoal-400'}`} />
            <span>Chat</span>
          </button>

          <button
            onClick={() => setCurrentTab('knowledge')}
            className={`flex flex-col items-center justify-center py-1 px-3 rounded-lg text-[10px] font-medium transition-colors ${
              currentTab === 'knowledge'
                ? 'text-gold-light'
                : 'text-charcoal-400 hover:text-charcoal-200'
            }`}
          >
            <BookOpen className={`w-4 h-4 mb-0.5 ${currentTab === 'knowledge' ? 'text-gold' : 'text-charcoal-400'}`} />
            <span>Materials</span>
          </button>

          <button
            onClick={() => setCurrentTab('quiz')}
            className={`flex flex-col items-center justify-center py-1 px-3 rounded-lg text-[10px] font-medium transition-colors ${
              currentTab === 'quiz'
                ? 'text-gold-light'
                : 'text-charcoal-400 hover:text-charcoal-200'
            }`}
          >
            <CheckCircle2 className={`w-4 h-4 mb-0.5 ${currentTab === 'quiz' ? 'text-gold' : 'text-charcoal-400'}`} />
            <span>Quiz</span>
          </button>

          <button
            onClick={() => setCurrentTab('dashboard')}
            className={`flex flex-col items-center justify-center py-1 px-3 rounded-lg text-[10px] font-medium transition-colors ${
              currentTab === 'dashboard'
                ? 'text-gold-light'
                : 'text-charcoal-400 hover:text-charcoal-200'
            }`}
          >
            <BarChart3 className={`w-4 h-4 mb-0.5 ${currentTab === 'dashboard' ? 'text-gold' : 'text-charcoal-400'}`} />
            <span>Progress</span>
          </button>
        </nav>
      </div>

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        profile={profile}
        onProfileUpdated={loadProfile}
      />
    </div>
  );
}

export default App;
