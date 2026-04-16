"use client";

import React from "react";
import { format } from "date-fns";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, ShieldAlert, ShieldCheck, Zap } from "lucide-react";

export default function LiveLogFeed({ logs }: { logs: any[] }) {
  if (!logs || logs.length === 0) {
    return (
      <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-6 flex flex-col items-center justify-center h-80 shadow-glass">
        <Activity className="w-8 h-8 text-white/10 mb-2 animate-pulse" />
        <span className="text-white/20 font-medium tracking-tight">Listening for security events...</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between mb-6 px-2">
        <h3 className="text-xs font-bold tracking-[0.3em] text-white/30 uppercase">
          Intelligence Stream
        </h3>
        <div className="flex items-center gap-3 text-[10px] font-bold text-emerald-400 uppercase tracking-[0.2em] bg-emerald-500/15 px-4 py-1.5 rounded-full border border-emerald-500/30 shadow-[0_0_10px_rgba(16,185,129,0.1)]">
          <div className="relative flex h-2 w-2">
             <div className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></div>
             <div className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500 shadow-[0_0_5px_rgba(16,185,129,0.5)]"></div>
          </div>
          Live Network
        </div>
      </div>

      <div className="flex flex-col gap-2 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
        <AnimatePresence initial={false}>
          {logs.map((log, i) => {
            const decision = log.decision || "allow";
            const isBlock = decision === "block";
            const isEscalate = decision === "escalate";
            
            return (
              <motion.div
                key={log.timestamp + i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                layout
                className="group relative bg-white/[0.03] border border-white/5 hover:border-white/10 backdrop-blur-md rounded-xl p-4 transition-all hover:bg-white/[0.06] shadow-sm overflow-hidden"
              >
                {/* Visual accent bar */}
                <div className={`absolute left-0 top-0 bottom-0 w-1 ${
                  isBlock ? "bg-red-500" : isEscalate ? "bg-amber-500" : "bg-emerald-500"
                }`} />

                <div className="flex items-start justify-between gap-4">
                   <div className="flex-1 min-w-0 space-y-2">
                      <div className="flex items-center gap-3">
                         <span className="text-[11px] font-mono text-white/30">{format(new Date(log.timestamp), "HH:mm:ss.SS")}</span>
                         <span className="px-1.5 py-0.5 rounded bg-white/5 text-[10px] font-mono text-white/50 tracking-tighter">
                            {log.event_id?.slice(0, 8) || "req_id"}
                         </span>
                         <span className={`text-[11px] font-bold uppercase tracking-[0.1em] ${
                             isBlock ? "text-red-400" : isEscalate ? "text-amber-400" : "text-emerald-400"
                         }`}>
                             {log.tier ? `Layer ${log.tier}` : "Core Guard"}
                         </span>
                      </div>
                      <p className="text-sm text-white/80 line-clamp-1 font-medium leading-tight">
                         {log.prompt}
                      </p>
                   </div>

                   <div className="flex flex-col items-end gap-2 shrink-0">
                      <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-lg border text-[10px] font-bold uppercase ${
                        isBlock 
                          ? "border-red-500/20 bg-red-500/10 text-red-400 shadow-[0_0_10px_rgba(239,68,68,0.1)]" 
                          : isEscalate 
                          ? "border-amber-500/20 bg-amber-500/10 text-amber-400 shadow-[0_0_10px_rgba(245,158,11,0.1)]" 
                          : "border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
                      }`}>
                         {isBlock ? <ShieldAlert size={10} /> : isEscalate ? <Activity size={10} /> : <ShieldCheck size={10} />}
                         {decision}
                      </div>
                      <div className="flex items-center gap-2 text-[11px]">
                         <span className="text-white/20 uppercase font-bold tracking-widest">Risk</span>
                         <span className={`font-mono text-sm font-bold ${log.risk_score > 0.6 ? "text-amber-400" : "text-white/70"}`}>
                            {log.risk_score.toFixed(3)}
                         </span>
                      </div>
                   </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
}

