"use client";

import React from "react";
import { Activity, ShieldAlert, Zap, Lock } from "lucide-react";

export default function MetricsGrid({ stats }: { stats: any }) {
  // Safe fallbacks
  const t = stats || {
    total_requests: 0,
    blocked: 0,
    escalated: 0,
    avg_risk_score: 0.0,
    avg_latency_ms: 0.0
  };

  const blockRate = t.total_requests > 0 
    ? ((t.blocked / t.total_requests) * 100).toFixed(1)
    : "0.0";

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
      
      {/* Metric 1 */}
      <div className="bg-black/60 border border-white/10 p-5 backdrop-blur flex flex-col gap-2 relative overflow-hidden group">
        <div className="absolute -right-4 -top-4 opacity-5 group-hover:opacity-10 transition-opacity">
          <Activity size={100} />
        </div>
        <span className="text-white/40 text-xs font-mono uppercase tracking-widest flex items-center gap-2">
          <Activity size={14} /> Total Analyzed
        </span>
        <div className="text-5xl font-black text-white mt-2">
          {t.total_requests}
        </div>
      </div>

      {/* Metric 2 */}
      <div className="bg-black/60 border border-red-500/20 p-5 backdrop-blur flex flex-col gap-2 relative overflow-hidden group">
         <div className="absolute -right-4 -top-4 opacity-5 group-hover:opacity-10 transition-opacity text-red-500">
          <ShieldAlert size={100} />
        </div>
        <span className="text-red-400/80 text-xs font-mono uppercase tracking-widest flex items-center gap-2">
          <ShieldAlert size={14} /> Prevented
        </span>
        <div className="flex items-end gap-3 mt-2">
           <div className="text-5xl font-black text-red-500">
            {t.blocked}
          </div>
          <div className="mb-2 text-sm font-mono text-red-400/50">({blockRate}%)</div>
        </div>
      </div>

      {/* Metric 3 */}
      <div className="bg-black/60 border border-yellow-500/20 p-5 backdrop-blur flex flex-col gap-2 relative overflow-hidden group">
         <div className="absolute -right-4 -top-4 opacity-5 group-hover:opacity-10 transition-opacity text-yellow-500">
          <Zap size={100} />
        </div>
        <span className="text-yellow-400/80 text-xs font-mono uppercase tracking-widest flex items-center gap-2">
          <Zap size={14} /> Avg ASI Risk
        </span>
        <div className="text-5xl font-black text-yellow-500 mt-2">
          {t.avg_risk_score.toFixed(2)}
        </div>
      </div>

       {/* Metric 4 */}
      <div className="bg-black/60 border border-white/10 p-5 backdrop-blur flex flex-col gap-2 relative overflow-hidden group">
         <div className="absolute -right-4 -top-4 opacity-5 group-hover:opacity-10 transition-opacity">
          <Lock size={100} />
        </div>
        <span className="text-white/40 text-xs font-mono uppercase tracking-widest flex items-center gap-2">
          <Lock size={14} /> Avg Latency
        </span>
        <div className="flex items-end gap-2 mt-2">
           <div className="text-5xl font-black text-white">
            {t.avg_latency_ms && t.avg_latency_ms > 0 ? t.avg_latency_ms.toFixed(1) : "0.0"}
          </div>
          <div className="mb-2 text-sm font-mono text-white/40">ms</div>
        </div>
      </div>

    </div>
  );
}
