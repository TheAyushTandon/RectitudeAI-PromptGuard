"use client";

import { cn } from "../../lib/utils";

import React, { useState, useEffect } from "react";
import { Sidebar, SidebarBody, SidebarLink } from "../../components/ui/sidebar";
import { motion } from "framer-motion";
import { FallingPattern } from "../../components/ui/falling-pattern";
import { LordIcon } from "../../components/ui/lord-icon";
import { ShieldCheck, Database, LayoutDashboard, BrainCog, Zap } from "lucide-react";
import Link from "next/link";
import SecurityCharts from "../../components/dashboard/SecurityCharts";
import LiveLogFeed from "../../components/dashboard/LiveLogFeed";
import DynamicThresholds from "../../components/dashboard/DynamicThresholds";
import { MetricCard } from "../../components/ui/metric-card";
import IncidentChart from "../../components/ui/incident-chart";
import { BGPattern } from "../../components/ui/bg-pattern";


export default function DashboardPage() {
  const [open, setOpen] = useState(false);
  const [stats, setStats] = useState(null);
  const [logs, setLogs] = useState([]);
  const [settings, setSettings] = useState(null);
  const [isConnected, setIsConnected] = useState(true);

  // Production-ready API Base
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const links = [
    { label: "Dashboard", href: "/dashboard", icon: <LayoutDashboard className="h-5 w-5 text-white/50" /> },
    { label: "Chat", href: "/chat", icon: <ShieldCheck className="h-5 w-5 text-white/50" /> },
  ];

  // Auto-polling effect
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, logsRes, settingsRes] = await Promise.all([
          fetch(`${API_BASE}/v1/dashboard/stats`),
          fetch(`${API_BASE}/v1/dashboard/logs?limit=10`),
          fetch(`${API_BASE}/v1/dashboard/settings`),
        ]);

        if (statsRes.ok && logsRes.ok && settingsRes.ok) {
          setStats(await statsRes.json());
          setLogs(await logsRes.json());
          setSettings(await settingsRes.json());
          setIsConnected(true);
        } else {
          setIsConnected(false);
        }
      } catch (err) {
        setIsConnected(false);
        console.warn("Dashboard Polling - Connection Lost (Backend Offline)");
      }
    };

    fetchData(); // initial fetch
    const interval = setInterval(fetchData, 1500);
    return () => clearInterval(interval);
  }, []);

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
          <div className="px-2 pb-4">
            <SidebarLink
              link={{
                label: "Profile", href: "/profile",
                icon: <LordIcon src="https://cdn.lordicon.com/kthelypq.json" trigger="hover" size={32} />
              }}
              className="hover:bg-white/5 rounded-lg p-2 transition-colors"
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

          <div className="z-10 w-full max-w-7xl flex flex-col gap-10 pt-4">
            {/* Premium Header Section */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                   <div className="h-1 w-12 bg-primary rounded-full shadow-[0_0_10px_rgba(255,255,255,0.3)]" />
                   <span className="text-[10px] font-bold tracking-[0.4em] text-white/40 uppercase">Command Center</span>
                </div>
                <h1 className="text-5xl md:text-6xl font-display tracking-[0.1em] text-white leading-none uppercase">Security Overview</h1>
              </div>
              
              <div className="flex items-center gap-6 bg-white/[0.03] border border-white/5 backdrop-blur-md px-5 py-3 rounded-2xl">
                 <div className="flex flex-col">
                    <span className="text-[10px] text-white/30 uppercase font-bold tracking-widest">Network Status</span>
                    <span className="text-xs text-white/70 font-mono">{API_BASE.replace("http://", "").replace("https://", "")}</span>
                 </div>
                 <div className="h-8 w-px bg-white/10" />
                 <div className="flex items-center gap-3">
                   <div className="relative flex h-3 w-3">
                    {isConnected ? (
                      <>
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]"></span>
                      </>
                    ) : (
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]"></span>
                    )}
                  </div>
                  <span className={cn("text-[10px] font-bold tracking-widest uppercase transition-colors", isConnected ? "text-white/50" : "text-red-500")}>
                    {isConnected ? "Live Feed" : "System Offline"}
                  </span>
                </div>
              </div>
            </div>

            {/* Metrics Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard 
                title="Total Requests" 
                value={stats?.total_requests ?? 0} 
                icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>} 
              />
              <MetricCard 
                title="Intercepted" 
                value={stats?.blocked ?? 0} 
                color="text-red-500"
                icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>} 
              />
              <MetricCard 
                title="ASI Agg Risk" 
                value={stats?.avg_risk_score?.toFixed(3) ?? '0.000'} 
                color="text-amber-500"
                icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01" /></svg>} 
              />
              <MetricCard 
                title="Compute Latency" 
                value={`${stats?.avg_latency_ms?.toFixed(1) ?? '0'}ms`} 
                icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>} 
              />
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 pb-12 w-full">
              <div className="lg:col-span-2 space-y-8 min-w-0 overflow-hidden">
                 <SecurityCharts stats={stats} logs={logs} />
                 <LiveLogFeed logs={logs} />
              </div>
              <div className="lg:col-span-1 min-w-0 overflow-hidden">
                 <div className="sticky top-10">
                    <DynamicThresholds settings={settings} />
                 </div>
              </div>
            </div>
          </div>
        </div>
      </Sidebar>
    </div>
  );
}
