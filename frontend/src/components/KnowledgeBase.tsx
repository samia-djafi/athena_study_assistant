import React, { useState } from 'react';
import {
  Upload,
  FileText,
  Trash2,
  RefreshCw,
  AlertTriangle,
  Info,
  CheckCircle,
  Clock,
  Layers,
  ArrowRight
} from 'lucide-react';
import { DocumentItem } from '../types';
import { uploadDocument, deleteDocument } from '../api';

interface KnowledgeBaseProps {
  documents: DocumentItem[];
  onRefreshDocs: () => void;
}

export const KnowledgeBase: React.FC<KnowledgeBaseProps> = ({
  documents,
  onRefreshDocs
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<'idle' | 'uploading' | 'processing' | 'ready'>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setIsUploading(true);
      setErrorMessage(null);
      setUploadProgress('uploading');

      // Simulate visual progression
      setTimeout(() => setUploadProgress('processing'), 500);
      await uploadDocument(file, 'guest');
      setUploadProgress('ready');

      setTimeout(() => {
        setIsUploading(false);
        setUploadProgress('idle');
        onRefreshDocs();
      }, 700);
    } catch (err: any) {
      setErrorMessage(err.message || 'Upload failed');
      setIsUploading(false);
      setUploadProgress('idle');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id, 'guest');
      onRefreshDocs();
    } catch (err) {
      console.error(err);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="flex-1 flex flex-col h-screen bg-charcoal-950 overflow-y-auto">
      {/* Header */}
      <header className="p-4 sm:p-6 border-b border-charcoal-800 bg-charcoal-900/60">
        <div className="flex flex-col sm:flex-row gap-3 sm:gap-0 items-start sm:items-center justify-between max-w-5xl mx-auto">
          <div>
            <h1 className="text-base sm:text-lg font-semibold text-charcoal-100 flex flex-wrap items-center gap-2">
              <FileText className="w-5 h-5 text-gold flex-shrink-0" />
              <span>Study Materials & Knowledge Base</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-gold/15 text-gold-light border border-gold/30 font-mono">
                RAG UI Prototype
              </span>
            </h1>
            <p className="text-xs text-charcoal-400 mt-1">
              Visual interface for course lecture notes, textbooks, and PDF learning materials.
            </p>
          </div>
          <button
            onClick={onRefreshDocs}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-charcoal-800 hover:bg-charcoal-700 text-charcoal-300 text-xs transition-colors border border-charcoal-700 self-end sm:self-auto"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </header>

      <div className="max-w-5xl mx-auto w-full p-3 sm:p-6 space-y-4 sm:space-y-6 pb-20 md:pb-6">
        {/* Specification Required Notice Banner */}
        <div className="p-3.5 sm:p-4 rounded-xl bg-charcoal-900 border border-gold/30 flex items-start gap-3">
          <Info className="w-5 h-5 text-gold flex-shrink-0 mt-0.5" />
          <div className="text-xs text-charcoal-300 leading-relaxed">
            <span className="font-semibold text-gold-light block mb-1">
              RAG UI Prototype — Backend Indexing Not Implemented
            </span>
            This workspace demonstrates the intended document ingestion and retrieval user experience.
            In accordance with system specifications, vector databases, document chunking, and embedding models
            are not connected. If asked about uploaded files in chat, Athena will explain that backend document
            answering is in prototype phase rather than inventing fabricated citations.
          </div>
        </div>

        {/* Upload Dropzone */}
        <div className="p-6 rounded-xl border-2 border-dashed border-charcoal-700 hover:border-gold/40 bg-charcoal-900/40 text-center transition-colors">
          <Upload className="w-8 h-8 text-gold mx-auto mb-2 opacity-80" />
          <h3 className="text-sm font-medium text-charcoal-200 mb-1">Upload Study Notes or PDFs</h3>
          <p className="text-xs text-charcoal-500 mb-4">Supported: PDF, TXT, Markdown (Max 15MB)</p>

          <label className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gold/15 text-gold-light border border-gold/30 hover:bg-gold/25 cursor-pointer text-xs font-medium transition-colors">
            <span>Select Document</span>
            <input
              type="file"
              onChange={handleFileUpload}
              accept=".pdf,.txt,.md"
              className="hidden"
              disabled={isUploading}
            />
          </label>

          {/* Visual Progression sequence: Uploaded -> Processing -> Ready */}
          {isUploading && (
            <div className="mt-6 p-4 rounded-lg bg-charcoal-850 border border-charcoal-700 max-w-md mx-auto">
              <div className="text-xs font-medium text-charcoal-300 mb-3">Document Processing Sequence</div>
              <div className="flex items-center justify-between text-[11px] text-charcoal-400">
                <span className={`flex items-center gap-1 ${uploadProgress !== 'idle' ? 'text-gold-light' : ''}`}>
                  <CheckCircle className="w-3.5 h-3.5" /> Uploaded
                </span>
                <ArrowRight className="w-3 h-3 text-charcoal-600" />
                <span className={`flex items-center gap-1 ${uploadProgress === 'processing' || uploadProgress === 'ready' ? 'text-gold-light' : ''}`}>
                  <Clock className="w-3.5 h-3.5 animate-spin" /> Processing
                </span>
                <ArrowRight className="w-3 h-3 text-charcoal-600" />
                <span className={`flex items-center gap-1 ${uploadProgress === 'ready' ? 'text-green-400' : ''}`}>
                  <CheckCircle className="w-3.5 h-3.5" /> Ready
                </span>
              </div>
            </div>
          )}

          {errorMessage && (
            <div className="mt-3 text-xs text-red-400 flex items-center justify-center gap-1">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>{errorMessage}</span>
            </div>
          )}
        </div>

        {/* Document Cards List */}
        <div>
          <h2 className="text-sm font-semibold text-charcoal-200 mb-3 flex items-center gap-2">
            <span>Indexed Study Materials</span>
            <span className="text-xs px-2 py-0.2 rounded bg-charcoal-800 text-charcoal-400 font-mono">
              {documents.length}
            </span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="p-4 rounded-xl bg-charcoal-900 border border-charcoal-800 hover:border-charcoal-700 transition-colors flex items-start justify-between"
              >
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-charcoal-800 border border-charcoal-700 flex items-center justify-center text-gold mt-0.5">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-medium text-charcoal-100 truncate max-w-xs">{doc.filename}</h4>
                    <div className="flex items-center gap-2 text-[11px] text-charcoal-400 mt-1">
                      <span>{formatSize(doc.size_bytes)}</span>
                      <span>•</span>
                      <span className="text-green-400/90 font-medium">{doc.status}</span>
                    </div>
                    <div className="text-[10px] text-charcoal-500 mt-2 italic">
                      {doc.note}
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(doc.id)}
                  className="p-1.5 text-charcoal-500 hover:text-red-400 transition-colors rounded hover:bg-charcoal-800"
                  title="Remove document"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Illustrative RAG Activity Panel */}
        <div className="p-4 rounded-xl bg-charcoal-900/50 border border-charcoal-800">
          <h3 className="text-xs font-semibold text-charcoal-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-gold" />
            <span>Illustrative RAG Retrieval Pipeline (Architecture Preview)</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs text-charcoal-400">
            <div className="p-3 rounded-lg bg-charcoal-850 border border-charcoal-800">
              <div className="font-medium text-gold-light mb-1">1. Query Decomposition</div>
              <p className="text-[11px]">Identifies semantic concepts from student prompts to formulate targeted vector queries.</p>
            </div>
            <div className="p-3 rounded-lg bg-charcoal-850 border border-charcoal-800">
              <div className="font-medium text-gold-light mb-1">2. Semantic Similarity</div>
              <p className="text-[11px]">Matches question representations against document chunks using cosine similarity.</p>
            </div>
            <div className="p-3 rounded-lg bg-charcoal-850 border border-charcoal-800">
              <div className="font-medium text-gold-light mb-1">3. Citation Grounding</div>
              <p className="text-[11px]">Returns verified source references with exact document titles and page metadata.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
