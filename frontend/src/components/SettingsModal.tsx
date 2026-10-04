import React, { useState } from 'react';
import {
  X,
  Settings,
  Shield,
  Trash2,
  Cpu,
  Check,
  Save,
  Globe
} from 'lucide-react';
import { LearningLevel, ExplanationDepth, LearnerProfile } from '../types';
import { updatePreferences, resetLearningProgress } from '../api';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  profile: LearnerProfile | null;
  onProfileUpdated: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  profile,
  onProfileUpdated
}) => {
  const [level, setLevel] = useState<LearningLevel>(profile?.preferred_level || 'intermediate');
  const [depth, setDepth] = useState<ExplanationDepth>(profile?.preferred_depth || 'standard');
  const [language, setLanguage] = useState(profile?.preferred_language || 'English');
  const [savedNotice, setSavedNotice] = useState(false);
  const [resetNotice, setResetNotice] = useState(false);

  if (!isOpen) return null;

  const handleSave = async () => {
    try {
      await updatePreferences('guest', {
        preferred_level: level,
        preferred_depth: depth,
        preferred_language: language
      });
      setSavedNotice(true);
      setTimeout(() => setSavedNotice(false), 2000);
      onProfileUpdated();
    } catch (err) {
      console.error(err);
    }
  };

  const handleResetData = async () => {
    if (window.confirm('Are you sure you want to clear your study history and reset your profile?')) {
      await resetLearningProgress('guest');
      setResetNotice(true);
      setTimeout(() => setResetNotice(false), 2000);
      onProfileUpdated();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-charcoal-900 border border-charcoal-700 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-charcoal-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-gold" />
            <h2 className="text-sm font-semibold text-charcoal-100">Learning Settings & Preferences</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-charcoal-400 hover:text-charcoal-100 hover:bg-charcoal-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6 overflow-y-auto max-h-[75vh]">
          {/* Pedagogical Defaults */}
          <div className="space-y-3">
            <h3 className="text-xs font-semibold text-charcoal-300 uppercase tracking-wider">
              Educational Defaults
            </h3>

            <div>
              <label className="block text-xs font-medium text-charcoal-400 mb-1.5">
                Default Learning Level
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(['beginner', 'intermediate', 'advanced'] as LearningLevel[]).map((lvl) => (
                  <button
                    key={lvl}
                    onClick={() => setLevel(lvl)}
                    className={`p-2 rounded-lg text-xs capitalize font-medium border transition-colors ${
                      level === lvl
                        ? 'bg-charcoal-800 text-gold-light border-gold/40'
                        : 'bg-charcoal-850 text-charcoal-400 border-charcoal-700/80 hover:bg-charcoal-800'
                    }`}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            </div>

            <div className="pt-2">
              <label className="block text-xs font-medium text-charcoal-400 mb-1.5">
                Default Explanation Depth
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(['short', 'standard', 'detailed'] as ExplanationDepth[]).map((d) => (
                  <button
                    key={d}
                    onClick={() => setDepth(d)}
                    className={`p-2 rounded-lg text-xs capitalize font-medium border transition-colors ${
                      depth === d
                        ? 'bg-charcoal-800 text-gold-light border-gold/40'
                        : 'bg-charcoal-850 text-charcoal-400 border-charcoal-700/80 hover:bg-charcoal-800'
                    }`}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>

            <div className="pt-2">
              <label className="block text-xs font-medium text-charcoal-400 mb-1.5">
                Preferred Language
              </label>
              <div className="flex items-center gap-2 bg-charcoal-850 border border-charcoal-700 rounded-lg px-3 py-2">
                <Globe className="w-4 h-4 text-charcoal-400" />
                <input
                  type="text"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="bg-transparent text-xs text-charcoal-100 flex-1 focus:outline-none"
                  placeholder="e.g. English, French, Spanish"
                />
              </div>
            </div>
          </div>

          {/* Connected Tools & Integrations */}
          <div className="space-y-3 pt-2 border-t border-charcoal-800">
            <h3 className="text-xs font-semibold text-charcoal-300 uppercase tracking-wider flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-gold" />
              <span>Connected Tools & Agent Subsystems</span>
            </h3>

            <div className="space-y-2 text-xs">
              <div className="p-2.5 rounded-lg bg-charcoal-850 border border-charcoal-800 flex items-center justify-between">
                <div>
                  <div className="font-medium text-charcoal-200">Web Research Provider</div>
                  <div className="text-[11px] text-charcoal-500">DuckDuckGo Search / Academic Filtering</div>
                </div>
                <span className="text-green-400 font-mono text-[11px]">Active</span>
              </div>

              <div className="p-2.5 rounded-lg bg-charcoal-850 border border-charcoal-800 flex items-center justify-between">
                <div>
                  <div className="font-medium text-charcoal-200">Safe Code Analysis Engine</div>
                  <div className="text-[11px] text-charcoal-500">AST Static Complexity & Security Linting</div>
                </div>
                <span className="text-green-400 font-mono text-[11px]">Isolated</span>
              </div>

              <div className="p-2.5 rounded-lg bg-charcoal-850 border border-charcoal-800 flex items-center justify-between">
                <div>
                  <div className="font-medium text-charcoal-200">Model Context Protocol (MCP) Client</div>
                  <div className="text-[11px] text-charcoal-500">athena-academic (ArXiv metadata lookup)</div>
                </div>
                <span className="text-green-400 font-mono text-[11px]">Enabled</span>
              </div>
            </div>
          </div>

          {/* Privacy & Data Controls */}
          <div className="space-y-3 pt-2 border-t border-charcoal-800">
            <h3 className="text-xs font-semibold text-charcoal-300 uppercase tracking-wider flex items-center gap-1.5">
              <Shield className="w-4 h-4 text-gold" />
              <span>Privacy & Learner Data Control</span>
            </h3>
            <p className="text-xs text-charcoal-400 leading-relaxed">
              Athena prioritizes privacy. Your sessions and quizzes are scoped to your learner profile.
              You can wipe all stored records at any time.
            </p>

            <button
              onClick={handleResetData}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-red-950/40 border border-red-800/40 text-red-300 hover:bg-red-900/40 text-xs font-medium transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Reset & Wipe Learning History</span>
            </button>
            {resetNotice && <span className="text-xs text-green-400 block">Study records cleared!</span>}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-charcoal-800 flex items-center justify-between bg-charcoal-850/60">
          {savedNotice ? (
            <span className="text-xs text-green-400 flex items-center gap-1 font-medium">
              <Check className="w-4 h-4" /> Preferences saved!
            </span>
          ) : (
            <span />
          )}

          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-charcoal-800 hover:bg-charcoal-700 text-charcoal-300 text-xs font-medium"
            >
              Close
            </button>
            <button
              onClick={handleSave}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-gold text-charcoal-950 hover:bg-gold-light text-xs font-medium shadow-sm"
            >
              <Save className="w-3.5 h-3.5" />
              <span>Save Preferences</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
