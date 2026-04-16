"use client";

import { cn } from "../../lib/utils";
import React, { useRef } from "react";

export function PromptInput({
  children,
  className,
  value,
  onValueChange,
  isLoading,
  onSubmit,
}: {
  children: React.ReactNode;
  className?: string;
  value: string;
  onValueChange: (val: string) => void;
  isLoading?: boolean;
  onSubmit: () => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);

  return (
    <div className={cn("relative flex flex-col w-full rounded-3xl border border-[#333333] bg-[rgba(10,10,10,0.85)] p-4 shadow-xl backdrop-blur-2xl transition-all focus-within:border-[#555555]", className)} ref={containerRef}>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          if (typeof child.type === "string") {
            return child;
          }
          // @ts-ignore
          return React.cloneElement(child, { value, onValueChange, onSubmit, isLoading });
        }
        return child;
      })}
    </div>
  );
}

export function PromptInputTextarea({
  value,
  onValueChange,
  onSubmit,
  placeholder = "Message Rectitude...",
}: {
  value?: string;
  onValueChange?: (val: string) => void;
  onSubmit?: () => void;
  placeholder?: string;
}) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (onSubmit) onSubmit();
    }
  };

  return (
    <textarea
      value={value}
      onChange={(e) => onValueChange?.(e.target.value)}
      onKeyDown={handleKeyDown}
      placeholder={placeholder}
      className="max-h-[200px] min-h-[44px] w-full resize-none bg-transparent px-2 py-1 text-sm text-[#E0E0E0] placeholder:text-[#666666] focus:outline-none"
      rows={1}
      style={{ overflowY: "auto" }}
    />
  );
}

export function PromptInputActions({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn("flex items-center", className)}>{children}</div>;
}

export function PromptInputAction({
  children,
  tooltip,
}: {
  children: React.ReactNode;
  tooltip?: string;
}) {
  return (
    <div className="relative group" title={tooltip}>
      {children}
    </div>
  );
}
