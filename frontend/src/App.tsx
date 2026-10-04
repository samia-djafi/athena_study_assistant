import React, { useState, useEffect } from 'react';
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
    <div className="flex h-screen bg-charcoal-950 font-sans text-charcoal-100 overflow-hidden">
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
      />

      <main className="flex-1 flex overflow-hidden">
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
