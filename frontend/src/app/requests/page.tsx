"use client";
import Header from "@/components/layout/Header";

export default function RequestInspector() {
  return (
    <div className="flex-1 flex flex-col h-full bg-background-dark">
      <Header title="Request Inspector" subtitle="Granular forensic analysis of individual LLM interactions" />
      <div className="flex-1 p-8 flex flex-col items-center justify-center opacity-30 select-none">
        <p className="font-mono text-xs uppercase tracking-[0.4em]">Forensic Engine Offline - Awaiting Integration</p>
      </div>
    </div>
  );
}
