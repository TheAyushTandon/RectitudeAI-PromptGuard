"use client";

import React, { useState } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

export function ChainOfThought({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn("flex flex-col gap-2 my-4", className)}>{children}</div>;
}

export function ChainOfThoughtStep({ children, className }: { children: React.ReactNode; className?: string }) {
  const [isOpen, setIsOpen] = useState(false);

  // We pass isOpen and setIsOpen to children by cloning them, or we can just manage state via context. 
  // Custom quick implementation:
  return (
    <div className={cn("border border-[rgba(123,63,228,0.2)] rounded-xl overflow-hidden bg-[rgba(38,38,38,0.4)] transition-all", className)}>
      <div
        className="cursor-pointer"
        onClick={() => setIsOpen(!isOpen)}
        data-state={isOpen ? "open" : "closed"}
      >
        {React.Children.map(children, (child) => {
          if (React.isValidElement(child)) {
            // @ts-ignore
            return React.cloneElement(child, { isOpen });
          }
          return child;
        })}
      </div>
    </div>
  );
}

export function ChainOfThoughtTrigger({
  leftIcon,
  children,
  isOpen,
}: {
  leftIcon?: React.ReactNode;
  children: React.ReactNode;
  isOpen?: boolean;
}) {
  return (
    <div className="flex items-center justify-between p-3 hover:bg-[rgba(123,63,228,0.05)] transition-colors">
      <div className="flex items-center gap-3">
        {leftIcon && <div className="text-[#A855F7]">{leftIcon}</div>}
        <span className="text-sm font-semibold text-[#F0EBF8]">{children}</span>
      </div>
      <ChevronDown
        className={cn("h-4 w-4 text-[#8B7AA0] transition-transform duration-300", isOpen && "rotate-180")}
      />
    </div>
  );
}

export function ChainOfThoughtContent({
  children,
  isOpen,
  className,
}: {
  children: React.ReactNode;
  isOpen?: boolean;
  className?: string;
}) {
  if (!isOpen) return null;

  return (
    <div className={cn("p-3 border-t border-[rgba(123,63,228,0.1)] bg-[#262626]/80", className)}>
      <ul className="flex flex-col gap-2 border-l-2 border-purple-900/30 ml-2 pl-4">
        {children}
      </ul>
    </div>
  );
}

export function ChainOfThoughtItem({ children }: { children: React.ReactNode }) {
  return (
    <li className="text-sm text-[#8B7AA0] leading-relaxed relative">
      <div className="absolute -left-[21px] top-2 h-1.5 w-1.5 rounded-full bg-[#A855F7]" />
      {children}
    </li>
  );
}
