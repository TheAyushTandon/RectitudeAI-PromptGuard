"use client";

import React, { useState } from "react";
import { Sidebar, SidebarBody, SidebarLink } from "@/components/ui/sidebar";
import { LayoutDashboard, ShieldCheck, User, Zap, Activity, Cpu, Database, Server } from "lucide-react";
import { cn } from "../../lib/utils";
import { motion } from "framer-motion";
import { BGPattern } from "@/components/ui/bg-pattern";

export default function SecurityPage() {
  const [open, setOpen] = useState(false);

  const links = [
    { label: "Dashboard", href: "/dashboard", icon: <LayoutDashboard className="h-5 w-5 text-white/50" /> },
    { label: "Chat", href: "/chat", icon: <ShieldCheck className="h-5 w-5 text-white/50" /> },
  ];

  const modelHealth = [
    { name: "Mistral 7B", status: "Healthy", latency: "88ms", load: "12%", type: "Primary Orchestrator" },
    { name: "Llama 3 (8B)", status: "Steady", latency: "142ms", load: "4%", type: "Reasoning Engine" },
    { name: "Phi-3 Mini", status: "Idle", latency: "0ms", load: "0%", type: "Edge Validator" },
    { name: "Neural Filter V2", status: "Healthy", latency: "12ms", load: "100%", type: "PII Scrubber" },
  ];

  const techStack = [
    { category: "Core Framework", items: ["Next.js 14 (App Router)", "FastAPI (Python 3.11)"] },
    { category: "Artificial Intelligence", items: ["Ollama Orchestration", "Multi-Agent Security Layer", "LangChain"] },
    { category: "Interface & Style", items: ["Tailwind CSS", "Framer Motion", "Lucide Icons"] },
    { category: "Storage & State", items: ["SQLite (Local DB)", "Zustand State Management"] },
  ];

  return (
    <div className="flex bg-[#050505] w-full min-h-screen text-white font-sans selection:bg-primary/30">
      <Sidebar open={open} setOpen={setOpen}>
        <SidebarBody className="justify-between gap-10 bg-white/[0.02] border-r border-white/5 backdrop-blur-xl">
          <div className="flex flex-col flex-1 overflow-y-auto overflow-x-hidden pt-4 px-2">
            <div className="flex items-center justify-center gap-3 mb-8 overflow-hidden">
               <div className="h-8 w-8 min-w-[2rem] flex items-center justify-center">
                  <img src="/logo.svg" alt="Rectitude.AI" className="w-full h-full object-contain" />
               </div>
               <motion.span 
                  animate={{ 
                    opacity: open ? 1 : 0,
                    width: open ? "auto" : 0,
                    display: open ? "inline-block" : "none"
                  }}
                  className="font-sans text-[11px] font-bold tracking-[0.4em] text-white uppercase whitespace-nowrap ml-1"
               >
                  Rectitude<span className="text-primary/50">.AI</span>
               </motion.span>
            </div>
            <div className="flex flex-col gap-1">
              {links.map((link, idx) => (
                <SidebarLink key={idx} link={link} className="hover:bg-white/5 rounded-lg py-3 px-4 transition-colors group" />
              ))}
            </div>
          </div>
          <div className="px-2 pb-4 border-t border-white/5 pt-4">
            <SidebarLink
              link={{
                label: "Profile", href: "/profile",
                icon: <div className="p-1 rounded bg-white/10"><User className="w-5 h-5 text-white" /></div>
              }}
              className="hover:bg-white/5 rounded-lg p-2 transition-colors border border-transparent"
            />
          </div>
        </SidebarBody>

        <div className="flex-1 flex flex-col items-start justify-start relative min-h-screen w-full p-8 md:p-16 overflow-y-auto">
          {/* Background */}
          <div className="fixed inset-0 z-0 pointer-events-none">
            <BGPattern 
              variant="checkerboard" 
              mask="fade-top" 
              size={64} 
              fill="rgba(255,255,255,0.01)" 
            />
          </div>

          <div className="z-10 w-full max-w-5xl space-y-20">
            {/* Page Header */}
            <div className="space-y-4">
              <h1 className="text-4xl font-semibold text-white tracking-tight">System Infrastructure & Health</h1>
              <p className="text-white/40 max-w-2xl leading-relaxed">
                A transparent breakdown of the models, logic layers, and technology stack powering the Rectitude.AI security gateway.
              </p>
            </div>

            {/* Model Health Section - No Containers */}
            <div className="space-y-8">
              <div className="flex items-center gap-3 text-primary/60">
                <Cpu className="w-5 h-5" />
                <h2 className="text-sm font-bold uppercase tracking-[0.2em]">Model Inventory & Real-time Health</h2>
              </div>
              
              <div className="space-y-4">
                {modelHealth.map((model, i) => (
                  <div key={i} className="flex flex-wrap items-center justify-between border-b border-white/5 pb-4 group hover:border-white/10 transition-colors">
                    <div className="flex items-center gap-6 min-w-[250px]">
                      <div className={cn(
                        "h-2 w-2 rounded-full",
                        model.status === "Healthy" ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" : 
                        model.status === "Steady" ? "bg-blue-500" : "bg-white/20"
                      )} />
                      <div className="flex flex-col">
                        <span className="text-lg font-medium text-white/90">{model.name}</span>
                        <span className="text-xs text-white/30">{model.type}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-12 text-sm">
                      <div className="flex flex-col items-end">
                        <span className="text-[10px] uppercase tracking-widest text-white/20 font-bold mb-1">Status</span>
                        <span className="font-medium text-white/70">{model.status}</span>
                      </div>
                      <div className="flex flex-col items-end w-20">
                        <span className="text-[10px] uppercase tracking-widest text-white/20 font-bold mb-1">Latency</span>
                        <span className="font-medium text-white/70">{model.latency}</span>
                      </div>
                      <div className="flex flex-col items-end w-20">
                        <span className="text-[10px] uppercase tracking-widest text-white/20 font-bold mb-1">Utilization</span>
                        <span className="font-medium text-white/70">{model.load}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Tech Stack Section - No Containers */}
            <div className="space-y-8">
              <div className="flex items-center gap-3 text-primary/60">
                <Server className="w-5 h-5" />
                <h2 className="text-sm font-bold uppercase tracking-[0.2em]">Platform Architecture</h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-16 gap-y-12">
                {techStack.map((category, i) => (
                  <div key={i} className="space-y-4 group">
                    <h3 className="text-xs font-bold text-white/20 uppercase tracking-[0.3em] group-hover:text-white/40 transition-colors">
                      {category.category}
                    </h3>
                    <div className="flex flex-wrap gap-2">
                       {category.items.map((item, j) => (
                         <span key={j} className="text-lg font-medium text-white/70 after:content-['/'] last:after:content-[''] after:mx-2 after:text-white/10">
                           {item}
                         </span>
                       ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Security Footnote */}
            <div className="pt-20 border-t border-white/5 opacity-20 hover:opacity-100 transition-opacity">
               <p className="text-[10px] font-mono tracking-[0.5em] uppercase text-center w-full">
                 Verified Immutable Environment — Operational Status Alpha
               </p>
            </div>
          </div>
        </div>
      </Sidebar>
    </div>
  );
}
