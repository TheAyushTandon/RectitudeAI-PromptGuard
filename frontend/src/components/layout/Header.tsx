"use client";

import { Send, ShieldAlert } from "lucide-react";

interface HeaderProps {
  title: string;
  subtitle?: string;
  showActionButton?: boolean;
  onAction?: () => void;
  actionLoading?: boolean;
}

export default function Header({ 
  title, 
  subtitle, 
  showActionButton = false, 
  onAction,
  actionLoading = false
}: HeaderProps) {
  return (
    <header className="h-16 flex-shrink-0 border-b border-muted/30 bg-surface flex items-center justify-between px-8 z-40">
      <div className="flex flex-col">
        <h2 className="text-xl font-bold tracking-tight uppercase text-text-main leading-tight">
          {title}
        </h2>
        {subtitle && (
          <p className="text-[11px] font-mono text-muted uppercase tracking-wider mt-0.5">
            {subtitle}
          </p>
        )}
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-3 font-mono text-[11px]">
          <span className="text-muted uppercase">Target Env:</span>
          <div className="flex items-center gap-2 border border-primary/30 px-3 py-1 bg-primary/5 shadow-[inset_0_0_8px_rgba(0,240,255,0.1)]">
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
            <span className="text-primary font-bold tracking-widest text-glow">STAGING-US-EAST</span>
          </div>
        </div>

        {showActionButton && (
          <button 
            onClick={onAction}
            disabled={actionLoading}
            className="h-10 px-6 bg-primary text-background-dark font-black text-[13px] uppercase tracking-widest hover:bg-white transition-all duration-300 flex items-center gap-3 shadow-neon-primary group disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {actionLoading ? (
              <div className="w-4 h-4 border-2 border-background-dark border-t-transparent rounded-full animate-spin" />
            ) : (
              <Send className="w-4 h-4 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
            )}
            <span>Run Attack Simulation</span>
          </button>
        )}
      </div>
    </header>
  );
}
