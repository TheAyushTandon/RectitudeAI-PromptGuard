"use client";

import { ReactNode } from "react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface StatCardProps {
  label: string;
  value: string | number;
  trend?: string;
  trendType?: "positive" | "negative" | "neutral";
  icon: ReactNode;
  color?: "primary" | "blocked" | "escalated" | "allowed";
}

export default function StatCard({ 
  label, 
  value, 
  trend, 
  trendType = "neutral", 
  icon,
  color = "primary" 
}: StatCardProps) {
  
  const colorMap = {
    primary: "border-primary/20 bg-primary/5 text-primary shadow-neon-primary",
    blocked: "border-blocked/20 bg-blocked/5 text-blocked shadow-neon-blocked",
    escalated: "border-escalated/20 bg-escalated/5 text-escalated shadow-neon-escalated",
    allowed: "border-allowed/20 bg-allowed/5 text-allowed shadow-neon-allowed",
  };

  const textColorMap = {
    primary: "text-primary",
    blocked: "text-blocked",
    escalated: "text-escalated",
    allowed: "text-allowed",
  };

  const trendColorMap = {
    positive: "text-allowed",
    negative: "text-blocked",
    neutral: "text-muted",
  };

  return (
    <div className="border border-muted/20 bg-surface p-5 flex flex-col justify-between h-[130px] transition-all duration-300 hover:border-muted/50 group relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
        {icon}
      </div>

      <div className="flex flex-col gap-1">
        <div className="text-[11px] font-bold text-muted uppercase tracking-widest flex items-center gap-2">
          <div className={cn("w-1 h-3", color === "primary" ? "bg-primary" : `bg-${color}`)} />
          {label}
        </div>
        <div className={cn("text-3xl font-black tracking-tight mt-2 font-mono", textColorMap[color])}>
          {value}
        </div>
      </div>

      {trend && (
        <div className={cn("text-[10px] font-mono font-bold uppercase tracking-wider", trendColorMap[trendType])}>
          {trend}
        </div>
      )}
    </div>
  );
}
