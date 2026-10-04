import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Sparkles,
  Search,
  Image,
  Code2,
  Copy,
  Check,
  ExternalLink,
  ShieldCheck,
  AlertCircle,
  GraduationCap
} from 'lucide-react';
import { Message, LearningLevel, ExplanationDepth, WebSource } from '../types';
import { MarkdownRenderer } from './MarkdownRenderer';
import { streamChatResponse } from '../api';

interface ChatWorkspaceProps {
  sessionId: string;
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  level: LearningLevel;
  setLevel: (l: LearningLevel) => void;
  depth: ExplanationDepth;
  setDepth: (d: ExplanationDepth) => void;
  onSessionUpdated: () => void;
}

export const ChatWorkspace: React.FC<ChatWorkspaceProps> = ({
  sessionId,
  messages,
  setMessages,
  level,
  setLevel,
  depth,
  setDepth,
  onSessionUpdated
}) => {
  const [input, setInput] = useState('');
  const [requireSearch, setRequireSearch] = useState(false);
  const [activeAgentStatus, setActiveAgentStatus] = useState<{ agent: string; text: string } | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, activeAgentStatus]);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        setImageFile(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSend = async () => {
    if ((!input.trim() && !imageFile) || isGenerating) return;

    const userMessageContent = input.trim();
    const userMsgId = `usr-${Date.now()}`;
    const assistantMsgId = `asst-${Date.now()}`;

    const newMessages: Message[] = [
      ...messages,
      {
        id: userMsgId,
        role: 'user',
        content: userMessageContent || 'Analyze uploaded diagram/code screenshot.',
        timestamp: Date.now()
      },
      {
        id: assistantMsgId,
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
        agent: 'Orchestrator Agent',
        isStreaming: true
      }
    ];

    setMessages(newMessages);
    setInput('');
    const currentImg = imageFile;
    setImageFile(null);
    setIsGenerating(true);
    setActiveAgentStatus({ agent: 'Orchestrator Agent', text: 'Analyzing inquiry...' });

    let accumulatedContent = '';
    let gatheredSources: WebSource[] = [];

    await streamChatResponse(
      {
        message: userMessageContent,
        sessionId,
        userId: 'guest',
        level,
        depth,
        requireSearch,
        imageData: currentImg || undefined
      },
      {
        onStatus: (agent, status) => {
          setActiveAgentStatus({ agent, text: status });
        },
        onToken: (token, agent) => {
          accumulatedContent += token;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMsgId
                ? { ...m, content: accumulatedContent, agent: agent || m.agent }
                : m
            )
          );
        },
        onSources: (sources) => {
          gatheredSources = sources;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMsgId ? { ...m, sources: gatheredSources } : m
            )
          );
        },
        onDone: () => {
          setIsGenerating(false);
          setActiveAgentStatus(null);
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMsgId ? { ...m, isStreaming: false } : m
            )
          );
          onSessionUpdated();
        },
        onError: (err) => {
          setIsGenerating(false);
          setActiveAgentStatus(null);
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMsgId
                ? {
                    ...m,
                    content: `⚠️ **Error encountered**: ${err}`,
                    isStreaming: false
                  }
                : m
            )
          );
        }
      }
    );
  };

  return (
    <div className="flex-1 flex flex-col h-screen bg-charcoal-950 overflow-hidden">
      {/* Top Controls Bar */}
      <header className="h-14 border-b border-charcoal-800 bg-charcoal-900/60 px-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="text-xs font-medium text-charcoal-400">Level:</div>
          <div className="flex bg-charcoal-850 rounded-md p-0.5 border border-charcoal-700">
            {(['beginner', 'intermediate', 'advanced'] as LearningLevel[]).map((lvl) => (
              <button
                key={lvl}
                onClick={() => setLevel(lvl)}
                className={`text-xs px-2.5 py-1 rounded capitalize font-medium transition-all ${
                  level === lvl
                    ? 'bg-charcoal-700 text-gold-light shadow-sm'
                    : 'text-charcoal-400 hover:text-charcoal-200'
                }`}
              >
                {lvl}
              </button>
            ))}
          </div>

          <div className="h-4 w-[1px] bg-charcoal-700 mx-1" />

          <div className="text-xs font-medium text-charcoal-400">Depth:</div>
          <div className="flex bg-charcoal-850 rounded-md p-0.5 border border-charcoal-700">
            {(['short', 'standard', 'detailed'] as ExplanationDepth[]).map((d) => (
              <button
                key={d}
                onClick={() => setDepth(d)}
                className={`text-xs px-2.5 py-1 rounded capitalize font-medium transition-all ${
                  depth === d
                    ? 'bg-charcoal-700 text-gold-light shadow-sm'
                    : 'text-charcoal-400 hover:text-charcoal-200'
                }`}
              >
                {d}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setRequireSearch(!requireSearch)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs border transition-colors ${
              requireSearch
                ? 'bg-gold/15 text-gold-light border-gold/40'
                : 'bg-charcoal-850 text-charcoal-400 border-charcoal-700 hover:text-charcoal-200'
            }`}
            title="Enable web research for this query"
          >
            <Search className="w-3.5 h-3.5" />
            <span>Web Research</span>
          </button>
        </div>
      </header>

      {/* Message Feed */}
      <div className="flex-1 overflow-y-auto px-4 md:px-12 py-6 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto py-12">
            <div className="w-12 h-12 rounded-xl bg-gold/10 border border-gold/30 flex items-center justify-center text-gold mb-4">
              <GraduationCap className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-semibold text-charcoal-100 mb-1">
              Welcome to Athena Study Assistant
            </h2>
            <p className="text-xs text-charcoal-400 mb-6 leading-relaxed">
              Your adaptive AI workspace for Computer Science and Artificial Intelligence.
              Select your level and depth above, ask any algorithmic concept, debug code, or request a practice quiz.
            </p>

            <div className="grid grid-cols-2 gap-2 w-full text-left">
              {[
                'Explain Binary Search Trees with Big-O complexity',
                'How does Transformer Scaled Dot-Product Attention work?',
                'Review time complexity of nested loops in Python',
                'Generate a practice quiz on Graph Traversals'
              ].map((suggestion, i) => (
                <button
                  key={i}
                  onClick={() => setInput(suggestion)}
                  className="p-2.5 rounded-lg border border-charcoal-800 bg-charcoal-900/40 text-xs text-charcoal-300 hover:bg-charcoal-800 hover:text-gold-light hover:border-gold/30 transition-all"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-3xl ${
                msg.role === 'user' ? 'ml-auto justify-end' : 'mr-auto justify-start'
              }`}
            >
              {msg.role === 'assistant' && (
                <div className="w-7 h-7 rounded-lg bg-gold/15 border border-gold/30 flex-shrink-0 flex items-center justify-center text-gold text-xs font-mono mt-0.5">
                  Α
                </div>
              )}

              <div
                className={`rounded-xl px-4 py-3 text-xs leading-relaxed max-w-2xl ${
                  msg.role === 'user'
                    ? 'bg-charcoal-800 text-charcoal-100 border border-charcoal-700'
                    : 'bg-charcoal-900 text-charcoal-200 border border-charcoal-800'
                }`}
              >
                {/* Assistant Agent Header & Copy Control */}
                {msg.role === 'assistant' && (
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-charcoal-800 text-[11px] text-charcoal-400">
                    <span className="font-medium text-gold/90">{msg.agent || 'Athena Tutor'}</span>
                    <button
                      onClick={() => handleCopy(msg.id, msg.content)}
                      className="flex items-center gap-1 hover:text-gold-light transition-colors"
                      title="Copy full answer"
                    >
                      {copiedId === msg.id ? (
                        <>
                          <Check className="w-3 h-3 text-green-400" />
                          <span className="text-green-400">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copy Answer</span>
                        </>
                      )}
                    </button>
                  </div>
                )}

                {/* Content */}
                {msg.role === 'user' ? (
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                ) : (
                  <MarkdownRenderer content={msg.content} />
                )}

                {/* Grounded Web Sources */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-charcoal-800">
                    <p className="text-[11px] font-medium text-charcoal-400 mb-2 flex items-center gap-1">
                      <Search className="w-3 h-3 text-gold" />
                      <span>Verified Technical Sources:</span>
                    </p>
                    <div className="space-y-1.5">
                      {msg.sources.map((s, idx) => (
                        <a
                          key={idx}
                          href={s.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-start justify-between p-2 rounded bg-charcoal-850 hover:bg-charcoal-800 border border-charcoal-700/60 transition-colors text-[11px]"
                        >
                          <div>
                            <div className="font-medium text-gold-light truncate max-w-sm">{s.title}</div>
                            <div className="text-charcoal-400 text-[10px] truncate max-w-md">{s.snippet}</div>
                          </div>
                          <ExternalLink className="w-3.5 h-3.5 text-charcoal-400 flex-shrink-0 ml-2 mt-0.5" />
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-7 h-7 rounded-lg bg-charcoal-700 flex-shrink-0 flex items-center justify-center text-charcoal-300 text-xs font-medium mt-0.5">
                  U
                </div>
              )}
            </div>
          ))
        )}

        {/* Live Agent Activity Status Banner */}
        {activeAgentStatus && (
          <div className="flex items-center gap-2.5 max-w-2xl p-2.5 rounded-lg bg-charcoal-900/80 border border-gold/30 text-xs text-charcoal-300 animate-pulse">
            <Sparkles className="w-4 h-4 text-gold flex-shrink-0" />
            <div>
              <span className="font-semibold text-gold-light mr-1.5">[{activeAgentStatus.agent}]</span>
              <span>{activeAgentStatus.text}</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <footer className="p-4 border-t border-charcoal-800 bg-charcoal-900/80">
        <div className="max-w-3xl mx-auto">
          {imageFile && (
            <div className="mb-2 flex items-center gap-2 p-1.5 bg-charcoal-800 border border-gold/30 rounded-md text-xs text-gold-light">
              <Image className="w-4 h-4 text-gold" />
              <span>Image attached for multimodal analysis</span>
              <button
                onClick={() => setImageFile(null)}
                className="ml-auto text-charcoal-400 hover:text-red-400"
              >
                ✕
              </button>
            </div>
          )}

          <div className="flex items-end gap-2 bg-charcoal-850 border border-charcoal-700 focus-within:border-gold/50 rounded-xl p-2 transition-colors">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleImageUpload}
              accept="image/*"
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-2 text-charcoal-400 hover:text-gold-light transition-colors rounded-lg hover:bg-charcoal-800"
              title="Upload image, diagram, or error screenshot"
            >
              <Image className="w-4 h-4" />
            </button>

            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask an AI/CS concept, paste code to review, or request a quiz..."
              rows={1}
              className="flex-1 bg-transparent resize-none text-xs text-charcoal-100 placeholder-charcoal-500 focus:outline-none max-h-32 min-h-[28px] py-1 leading-normal"
            />

            <button
              onClick={handleSend}
              disabled={(!input.trim() && !imageFile) || isGenerating}
              className={`p-2 rounded-lg transition-all ${
                input.trim() || imageFile
                  ? 'bg-gold text-charcoal-950 hover:bg-gold-light shadow-sm'
                  : 'bg-charcoal-800 text-charcoal-600 cursor-not-allowed'
              }`}
              title="Send question"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>

          <div className="flex items-center justify-between mt-2 px-1 text-[11px] text-charcoal-500">
            <span>Press Enter to send, Shift+Enter for new line</span>
            <span className="flex items-center gap-1 text-[10px]">
              <ShieldCheck className="w-3 h-3 text-gold/70" />
              <span>Isolated execution • Zero host risk</span>
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
};
