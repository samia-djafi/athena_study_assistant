import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Copy, Check } from 'lucide-react';

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <div className="prose prose-invert max-w-none text-charcoal-200 text-sm leading-relaxed">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';
            const codeString = String(children).replace(/\n$/, '');

            if (!inline && language) {
              return <CodeBlock language={language} code={codeString} />;
            }
            return (
              <code className="bg-charcoal-800 text-gold-light px-1.5 py-0.5 rounded font-mono text-xs border border-charcoal-700" {...props}>
                {children}
              </code>
            );
          },
          h1: ({ children }) => <h1 className="text-xl font-semibold text-charcoal-100 border-b border-charcoal-700 pb-2 mb-3 mt-4">{children}</h1>,
          h2: ({ children }) => <h2 className="text-lg font-semibold text-charcoal-100 border-b border-charcoal-800 pb-1 mb-2 mt-3">{children}</h2>,
          h3: ({ children }) => <h3 className="text-base font-medium text-gold-light mb-2 mt-3">{children}</h3>,
          p: ({ children }) => <p className="mb-3 leading-relaxed">{children}</p>,
          ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>,
          li: ({ children }) => <li className="text-charcoal-300">{children}</li>,
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-gold pl-3 py-1 my-3 bg-charcoal-900/60 text-charcoal-300 italic rounded-r text-xs">
              {children}
            </blockquote>
          ),
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer" className="text-gold hover:text-gold-light underline underline-offset-2">
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

const CodeBlock: React.FC<{ language: string; code: string }> = ({ language, code }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-3 rounded-lg overflow-hidden border border-charcoal-700 bg-charcoal-900">
      <div className="flex items-center justify-between px-3 py-1.5 bg-charcoal-850 border-b border-charcoal-700/80 text-xs">
        <span className="font-mono text-charcoal-400 uppercase tracking-wider">{language}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 text-charcoal-400 hover:text-gold-light transition-colors py-0.5 px-2 rounded hover:bg-charcoal-800"
          title="Copy code"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>
      <pre className="p-3 overflow-x-auto text-xs font-mono text-charcoal-100 leading-normal">
        <code>{code}</code>
      </pre>
    </div>
  );
};
