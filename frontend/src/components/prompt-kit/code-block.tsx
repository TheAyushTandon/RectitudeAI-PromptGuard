"use client";

import { Check, Copy } from "lucide-react";
import { useState } from "react";
import { cn } from "../../lib/utils";

// Make sure to match CSS themes or just basic syntax highlighting
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/cjs/styles/prism";

export function CodeBlock({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("overflow-hidden rounded-xl border border-[rgba(123,63,228,0.2)] bg-[#262626]", className)}>
      {children}
    </div>
  );
}

export function CodeBlockCode({ code, language }: { code: string; language: string }) {
  const [copied, setCopied] = useState(false);

  const onCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group">
      <div className="flex items-center justify-between px-4 py-2 border-b border-[rgba(123,63,228,0.15)] bg-[#1A1A1A]">
        <span className="text-xs font-mono text-[#8B7AA0]">{language}</span>
        <button
          onClick={onCopy}
          className="p-1 hover:bg-[rgba(123,63,228,0.1)] rounded transition-colors text-[#8B7AA0] hover:text-[#F0EBF8]"
        >
          {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
        </button>
      </div>
      <div className="p-4 overflow-x-auto text-sm scrollbar-thin scrollbar-thumb-[rgba(123,63,228,0.3)]">
        <SyntaxHighlighter
          language={language}
          style={vscDarkPlus}
          customStyle={{ margin: 0, padding: 0, background: "transparent" }}
          codeTagProps={{ style: { fontFamily: "var(--font-mono)", fontSize: "0.875rem" } }}
        >
          {code}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}

// Provided helper for direct rendering
export function CodeBlockBasic({ code, language }: { code: string; language: string }) {
  return (
    <div className="w-full max-w-4xl my-4">
      <CodeBlock>
        <CodeBlockCode code={code} language={language} />
      </CodeBlock>
    </div>
  );
}
