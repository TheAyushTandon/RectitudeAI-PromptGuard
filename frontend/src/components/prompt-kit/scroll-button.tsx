"use client";

import { ChevronDown } from "lucide-react";
import { cn } from "../../lib/utils";

export function ScrollButton({ onClick, className }: { onClick?: () => void; className?: string }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex h-8 w-8 items-center justify-center rounded-full border border-[rgba(123,63,228,0.3)] bg-[rgba(13,0,25,0.8)] text-[#F0EBF8] shadow-lg backdrop-blur-sm transition-all hover:bg-[rgba(123,63,228,0.2)] hover:text-white",
        className
      )}
      aria-label="Scroll to bottom"
    >
      <ChevronDown className="h-4 w-4" />
    </button>
  );
}
