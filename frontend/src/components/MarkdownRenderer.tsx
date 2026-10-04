import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { Copy, Check } from 'lucide-react';

interface MarkdownRendererProps {
  content: string;
}

/**
 * Preprocesses raw markdown output from LLMs to fix common formatting issues:
 * 1. Cleans up "python\nCopy\n" artifacts into proper fenced code blocks.
 * 2. Converts tab-separated table rows into standard Markdown tables with pipes.
 * 3. Normalizes LaTeX math blocks and wraps un-delimited equations in $$ ... $$.
 * 4. Cleans up inner mismatched dollar signs within complex LaTeX equations.
 */
function normalizeMarkdownContent(raw: string): string {
  if (!raw) return '';

  let text = raw;

  // 1. UNICODE NORMALIZATION:
  // Convert mathematical/typographic lookalikes to standard ASCII markdown:
  // - Unicode vertical bars: ∣ (U+2223 divides), │ (U+2502 box vertical), ｜ (U+FF5C fullwidth) -> ASCII '|'
  text = text.replace(/[\u2223\u2502\uff5c]/g, '|');

  // - Unicode asterisks: ∗ (U+2217 asterisk operator), ﹡ (U+FE61), ＊ (U+FF0A) -> ASCII '*'
  text = text.replace(/[\u2217\ufe61\uff0a]/g, '*');

  // - Non-breaking hyphens (U+2011) -> ASCII '-'
  text = text.replace(/\u2011/g, '-');

  // - Unicode minuses & dashes (minus − U+2212, em-dash — U+2014, en-dash – U+2013) in dividers
  text = text.replace(/(?:^|\n)\s*[−—–-]{3,}\s*(?:\n|$)/g, '\n\n---\n\n');

  // 2. Fix smashed table rows where rows are concatenated with "||" or "| |":
  // e.g. "| O(1) | | Delete |" -> "| O(1) |\n| Delete |"
  text = text.replace(/\|\s*\|\s*([A-Za-z0-9_*$])/g, '|\n| $1');

  // 3. Fix headers crammed together with dividers or code blocks:
  // e.g. "--- ## Example:" -> "---\n\n## Example:"
  text = text.replace(/---\s*(#{1,4}\s+[^\n]+)/g, '---\n\n$1\n');
  text = text.replace(/([^\n])\s*(```(?:python|py|cpp|c|java|js|ts|go|rust|bash|sql|json|markdown))/gi, '$1\n\n$2\n');
  text = text.replace(/(```)\s*(#{1,4}\s+[^\n]+)/g, '$1\n\n$2\n');

  // 4. Fix "python\n\nCopy\n" artifact from model outputs
  text = text.replace(/(?:^|\n)(?:python|py)\s*\n+Copy\s*\n+/gi, '\n```python\n');

  // 5. Normalizing Big-O and asymptotic complexity notation outside math mode:
  // e.g. O\log n -> $O(\log n)$
  // h=Θ\log n -> $h = \Theta(\log n)$
  // h=O\log n -> $h = O(\log n)$
  // (O)logn -> $O(\log n)$
  text = text.replace(/\(O\)\s*log\s*n/gi, '$O(\\log n)$');
  text = text.replace(/([hkn]\s*=\s*)(?:Θ|\\Theta)\s*\\?log\s*([a-zA-Z0-9]+)/g, '$1$\\Theta(\\log $2)$');
  text = text.replace(/([hkn]\s*=\s*)O\s*\\?log\s*([a-zA-Z0-9]+)/g, '$1$O(\\log $2)$');
  text = text.replace(/\b(?:Θ|\\Theta)\s*\\?log\s*([a-zA-Z0-9]+)/g, '$\\Theta(\\log $1)$');
  text = text.replace(/\bO\\log\s*([a-zA-Z0-9]+)/g, '$O(\\log $1)$');

  // 6. Fix tab-separated and hybrid Markdown tables:
  const lines = text.split('\n');
  const processedLines: string[] = [];
  let inTable = false;

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];

    // If line has tabs, convert to pipe-delimited table cells
    if (line.includes('\t')) {
      const parts = line.split('\t').map(p => p.trim()).filter(Boolean);
      if (parts.length >= 2) {
        line = '| ' + parts.join(' | ') + ' |';
      }
    }

    // Check if line looks like a table row (starts/ends with pipe or has multiple pipes)
    const trimmed = line.trim();
    if (trimmed.startsWith('|') && trimmed.endsWith('|') && trimmed.length > 2) {
      if (!inTable) {
        inTable = true;
        processedLines.push(line);
        // Check if next line is already a divider row
        const nextLine = (i + 1 < lines.length) ? lines[i + 1].trim() : '';
        const isDivider = nextLine.startsWith('|') && /^\|[\s\-:|]+\|$/.test(nextLine);
        if (!isDivider) {
          // Generate appropriate divider row matching column count
          const colCount = (line.match(/\|/g) || []).length - 1;
          const divider = '| ' + Array(Math.max(colCount, 1)).fill('---').join(' | ') + ' |';
          processedLines.push(divider);
        }
        continue;
      }
      processedLines.push(line);
      continue;
    }

    inTable = false;
    processedLines.push(line);
  }
  text = processedLines.join('\n');

  // 7. Fix LLM artifact: variables/expressions wrapped in $ signs inside formulas
  // e.g. \mathcal{R}_N$\boldsymbol\theta$ -> \mathcal{R}_N(\boldsymbol\theta)
  text = text.replace(/([A-Za-z0-9}_\\;])\s*\$\s*(\\?[A-Za-z0-9_{}^,\s]+?)\s*\$/g, '$1($2)');
  text = text.replace(/([_\^]\{[^{}]*\})/g, (sub) => sub.replace(/\$/g, ''));
  text = text.replace(/_\s*\$\s*([^$\n]+?)\s*\$/g, '_{$1}');

  // 8. Convert explicit LaTeX display math \[ ... \] to $$ ... $$
  text = text.replace(/\\\[([\s\S]*?)\\\]/g, (_, math) => {
    const cleaned = math.replace(/\$/g, '').trim();
    return `\n$$\n${cleaned}\n$$\n`;
  });

  // 9. Convert explicit LaTeX inline math \( ... \) to $ ... $
  text = text.replace(/\\\(([\s\S]*?)\\\)/g, (_, math) => {
    const cleaned = math.replace(/\$/g, '').trim();
    return `$${cleaned}$`;
  });

  // 10. Wrap standalone lines that start with un-delimited LaTeX equations:
  // e.g. lines starting with \min, \max, \arg\min, \theta, \sum, \prod, \mathbb, \mathbf, \boldsymbol
  text = text.replace(
    /(?:^|\n)\s*(\\(?:arg\\min|arg\\max|min|max|theta|mathcal|hat|sum|mathbb|prod|mathbf|boldsymbol|frac|begin|Omega|int|partial|alpha|beta|gamma|delta|sigma|lambda|nabla|lim|inf|sup)[^\n]+)(?:\n|$)/g,
    (match, mathLine) => {
      if (mathLine.trim().startsWith('$$') && mathLine.trim().endsWith('$$')) {
        return match;
      }
      const cleaned = mathLine.replace(/\$/g, '').trim();
      return `\n\n$$\n${cleaned}\n$$\n\n`;
    }
  );

  // 11. Convert standalone bracketed display math [ \command ... ] to $$ ... $$
  text = text.replace(
    /(?:^|\n)\s*\[\s*([\s\S]*?\\(?:mathcal|mathbf|theta|prod|sum|frac|begin|sqrt|text|aligned|int|partial|alpha|beta|gamma|lambda|sigma|Omega|Theta|left|right|dots|circ|times|cdot|in|to|infty|min|max|boldsymbol)[\s\S]*?)\s*\]\s*(?:\n|$)/g,
    (_, math) => {
      const cleaned = math.replace(/\$/g, '').trim();
      return `\n\n$$\n${cleaned}\n$$\n\n`;
    }
  );

  // 12. Convert bracketed inline math ( \command ... ) to $ ... $
  text = text.replace(
    /\(\s*(\\[A-Za-z]+(?:\{[^}]*\}|\[[^\]]*\])*[^()\n]*?)\s*\)/g,
    (_, math) => {
      const cleaned = math.replace(/\$/g, '').trim();
      return `$${cleaned}$`;
    }
  );

  // 13. Convert single symbols in parentheses: (\theta), (\phi), (\pi), (\epsilon), (\lambda), (\mathbf{x}), (\mathbf{y})
  text = text.replace(
    /\(\s*(\\theta|\\phi|\\pi|\\epsilon|\\lambda|\\mu|\\sigma|\\alpha|\\beta|\\gamma|\\delta|\\eta|\\tau|\\omega|\\mathbf\{[A-Za-z0-9]+\}|[A-Za-z]_[A-Za-z0-9]+)\s*\)/g,
    '$$$1$$'
  );

  // 14. Global sanitization pass on all $$ ... $$ display blocks:
  // Remove any remaining '$' inside display math (strictly illegal in KaTeX/LaTeX math mode)
  text = text.replace(/\$\$([\s\S]*?)\$\$/g, (_, math) => {
    let cleaned = math.replace(/([A-Za-z0-9}_\\;])\s*\$\s*(\\?[A-Za-z0-9_{}^,\s]+?)\s*\$/g, '$1($2)');
    cleaned = cleaned.replace(/\$/g, '').trim();
    return `\n\n$$\n${cleaned}\n$$\n\n`;
  });

  return text;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  const normalizedContent = normalizeMarkdownContent(content);

  return (
    <div className="prose prose-invert max-w-none text-charcoal-200 text-xs sm:text-sm leading-relaxed overflow-hidden">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[
          [rehypeKatex, { output: 'html', throwOnError: false, errorColor: '#c5a059' }]
        ]}
        components={{
          code({ node, inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';
            const codeString = String(children).replace(/\n$/, '');

            if (!inline && (language || codeString.includes('\n'))) {
              return <CodeBlock language={language || 'code'} code={codeString} />;
            }
            return (
              <code
                className="bg-charcoal-800 text-gold-light px-1.5 py-0.5 rounded font-mono text-xs border border-charcoal-700/80"
                {...props}
              >
                {children}
              </code>
            );
          },
          h1: ({ children }) => (
            <h1 className="text-lg sm:text-xl font-semibold text-charcoal-100 border-b border-charcoal-700/80 pb-2 mb-3 mt-5 tracking-tight">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-base sm:text-lg font-semibold text-charcoal-100 border-b border-charcoal-800 pb-1.5 mb-2 mt-4 tracking-tight">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-sm sm:text-base font-medium text-gold-light mb-2 mt-3.5 tracking-tight">
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-xs sm:text-sm font-semibold text-charcoal-300 uppercase tracking-wider mb-1.5 mt-3">
              {children}
            </h4>
          ),
          p: ({ children }) => <p className="mb-3 leading-relaxed text-charcoal-200">{children}</p>,
          ul: ({ children }) => <ul className="list-disc list-outside ml-4 mb-3 space-y-1 text-charcoal-300">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-outside ml-4 mb-3 space-y-1 text-charcoal-300">{children}</ol>,
          li: ({ children }) => <li className="pl-1 leading-relaxed">{children}</li>,
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-gold pl-3.5 py-1.5 my-3 bg-charcoal-900/60 text-charcoal-300 italic rounded-r text-xs">
              {children}
            </blockquote>
          ),
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gold hover:text-gold-light underline underline-offset-2 transition-colors font-medium"
            >
              {children}
            </a>
          ),
          table: ({ children }) => (
            <div className="my-4 overflow-x-auto rounded-lg border border-charcoal-700 bg-charcoal-900/90 shadow-sm">
              <table className="min-w-full divide-y divide-charcoal-700 text-left text-xs">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-charcoal-850 text-gold-light font-medium uppercase tracking-wider text-[11px]">
              {children}
            </thead>
          ),
          tbody: ({ children }) => (
            <tbody className="divide-y divide-charcoal-800/80 bg-charcoal-900">
              {children}
            </tbody>
          ),
          tr: ({ children }) => (
            <tr className="hover:bg-charcoal-850/50 transition-colors">
              {children}
            </tr>
          ),
          th: ({ children }) => (
            <th className="px-3.5 py-2.5 font-semibold text-charcoal-200">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-3.5 py-2 text-charcoal-300 leading-normal">
              {children}
            </td>
          ),
          hr: () => <hr className="my-4 border-charcoal-800" />,
        }}
      >
        {normalizedContent}
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
    <div className="my-3.5 rounded-lg overflow-hidden border border-charcoal-700 bg-charcoal-900 shadow-md">
      <div className="flex items-center justify-between px-3.5 py-1.5 bg-charcoal-850 border-b border-charcoal-700/80 text-xs">
        <span className="font-mono text-gold/90 uppercase tracking-wider text-[11px] font-medium">
          {language}
        </span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 text-charcoal-400 hover:text-gold-light transition-colors py-0.5 px-2 rounded hover:bg-charcoal-800 text-[11px]"
          title="Copy code snippet"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>
      <pre className="p-3.5 overflow-x-auto text-xs font-mono text-charcoal-100 leading-relaxed bg-charcoal-950/70">
        <code>{code}</code>
      </pre>
    </div>
  );
};
