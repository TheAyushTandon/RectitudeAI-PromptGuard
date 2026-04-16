"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "../../lib/utils";
import { CodeBlockBasic } from "./code-block";

interface MarkdownProps {
  children: string;
  className?: string;
}

export function Markdown({ children, className }: MarkdownProps) {
  return (
    <div
      className={cn(
        "prose prose-invert max-w-none prose-p:leading-relaxed prose-pre:p-0 prose-pre:bg-transparent",
        className
      )}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          table({ children }) {
            return (
              <div className="my-6 w-full overflow-hidden border border-white/10 bg-white/[0.02] backdrop-blur-md shadow-2xl">
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse text-left text-base">
                    {children}
                  </table>
                </div>
              </div>
            );
          },
          thead({ children }) {
            return (
              <thead className="border-b border-white/10 bg-white/[0.05] text-xs uppercase tracking-[0.2em] font-mono text-white/90">
                {children}
              </thead>
            );
          },
          th({ children }) {
            return (
              <th className="px-6 py-4 font-bold border-r border-white/5 last:border-r-0">
                {children}
              </th>
            );
          },
          td({ children }) {
            return (
              <td className="px-6 py-4 border-t border-white/[0.03] border-r border-white/5 last:border-r-0 text-white/70 font-medium whitespace-nowrap">
                {children}
              </td>
            );
          },
          tr({ children }) {
            return (
              <tr className="transition-colors hover:bg-white/[0.03] group">
                {children}
              </tr>
            );
          },
          code({ node, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            const isInline = !match && !className?.includes("language-");

            if (isInline) {
              return (
                <code
                  className="bg-purple-500/10 text-purple-200 px-1.5 py-0.5 rounded text-sm font-mono border border-purple-500/20"
                  {...props}
                >
                  {children}
                </code>
              );
            }

            return (
              <CodeBlockBasic
                code={String(children).replace(/\n$/, "")}
                language={match ? match[1] : "text"}
              />
            );
          },
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}

