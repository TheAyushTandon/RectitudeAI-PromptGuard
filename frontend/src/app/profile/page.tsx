"use client";

import React, { useState } from "react";
import { Sidebar, SidebarBody, SidebarLink } from "@/components/ui/sidebar";
import { LayoutDashboard, ShieldCheck, User, Mail, Shield, Key, History } from "lucide-react";
import { cn } from "@/utils-lib/utils";
import { motion } from "framer-motion";
import { BGPattern } from "@/components/ui/bg-pattern";

export default function ProfilePage() {
  const [open, setOpen] = useState(false);

  const links = [
    { label: "Dashboard", href: "/dashboard", icon: <LayoutDashboard className="h-5 w-5 text-white/50" /> },
    { label: "Chat", href: "/chat", icon: <ShieldCheck className="h-5 w-5 text-white/50" /> },
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
              className="bg-white/5 rounded-lg p-2 transition-colors border border-white/5"
            />
          </div>
        </SidebarBody>

        <div className="flex-1 flex flex-col items-center justify-start relative min-h-screen w-full p-6 md:p-10 scroll-smooth">
          {/* Enhanced Background with Checkerboard & Masks */}
          <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
            <BGPattern 
              variant="checkerboard" 
              mask="fade-top" 
              size={64} 
              fill="rgba(255,255,255,0.02)" 
              className="opacity-100"
            />
          </div>

          <div className="z-10 w-full max-w-4xl flex flex-col gap-10 pt-4">
            {/* Header Section */}
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                 <div className="h-1 w-12 bg-primary rounded-full shadow-[0_0_10px_rgba(255,255,255,0.3)]" />
                 <span className="text-[10px] font-bold tracking-[0.4em] text-white/40 uppercase">Account Settings</span>
              </div>
              <h1 className="text-5xl font-display tracking-[0.1em] text-white leading-none uppercase">Personnel Profile</h1>
            </div>

            {/* Personnel Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {[
                {
                  name: "Ayush",
                  email: "ayush@rectitude.ai",
                  role: "Lead Security Architect",
                  accessLevel: "Level 5 - SuperAdmin",
                  status: "Active",
                  id: "RA-992-PX-10",
                  created: "Jan 12, 2026"
                },
                {
                  name: "Vartika",
                  email: "vartika@rectitude.ai",
                  role: "Security Intelligence Analyst",
                  accessLevel: "Level 4 - Data Sentinel",
                  status: "Active",
                  id: "RA-884-VX-09",
                  created: "Feb 14, 2026"
                }
              ].map((person, i) => (
                <div key={i} className="flex flex-col gap-6 group">
                  <div className="bg-white/[0.03] border border-white/10 backdrop-blur-md rounded-2xl p-8 shadow-glass relative overflow-hidden transition-all hover:bg-white/[0.05] hover:border-white/20">
                    <div className="flex items-start justify-between mb-8">
                      <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-primary/10 to-primary/30 p-0.5 relative flex items-center justify-center">
                        <div className="w-full h-full rounded-2xl bg-[#0a0a0a] flex items-center justify-center border border-white/10">
                          <User className="w-10 h-10 text-white/20" />
                        </div>
                        <div className="absolute -bottom-1 -right-1 h-4 w-4 rounded-full bg-emerald-500 border-2 border-[#050505]" />
                      </div>
                      <div className="text-right">
                        <span className="text-[10px] font-bold text-white/30 uppercase tracking-[0.2em]">Record ID</span>
                        <p className="text-sm font-mono text-white/60 font-bold">{person.id}</p>
                      </div>
                    </div>

                    <div className="space-y-1 mb-8">
                      <h2 className="text-2xl font-bold font-sans text-white tracking-tight">{person.name}</h2>
                      <p className="text-[10px] font-bold tracking-[0.3em] text-primary/70 uppercase">{person.role}</p>
                    </div>

                    <div className="grid grid-cols-1 gap-4 pt-6 border-t border-white/5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Mail className="w-3.5 h-3.5 text-white/20" />
                          <span className="text-[10px] font-bold text-white/30 uppercase tracking-widest">Endpoint</span>
                        </div>
                        <span className="text-sm font-medium text-white/80">{person.email}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Shield className="w-3.5 h-3.5 text-white/20" />
                          <span className="text-[10px] font-bold text-white/30 uppercase tracking-widest">Clearance</span>
                        </div>
                        <span className="text-sm font-medium text-white/80">{person.accessLevel}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <History className="w-3.5 h-3.5 text-white/20" />
                          <span className="text-[10px] font-bold text-white/30 uppercase tracking-widest">Onboarded</span>
                        </div>
                        <span className="text-sm font-medium text-white/80">{person.created}</span>
                      </div>
                    </div>

                    <div className="mt-8 flex gap-3">
                       <button className="flex-1 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-[10px] font-bold uppercase tracking-widest text-white/40 hover:bg-white/10 hover:text-white transition-all">
                          Edit Core Data
                       </button>
                       <button className="px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white/40 hover:bg-white/10 hover:text-white transition-all">
                          <Key className="w-4 h-4" />
                       </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Sidebar>
    </div>
  );
}
