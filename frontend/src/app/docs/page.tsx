"use client";

import React, { useState } from "react";
import { Shield, LayoutDashboard, Key, Activity, Zap } from "lucide-react";
import { Navbar, NavBody, NavItems, NavbarLogo, NavbarButton, MobileNav, MobileNavHeader, MobileNavMenu, MobileNavToggle } from "../../components/ui/resizable-navbar";
import { FooterSection } from "../../components/ui/footer-section";
import { TextEffect } from "../../components/ui/text-effect";
import { Marquee, DocsBadge } from "../../components/ui/docs-marquee";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, LineChart, Line, ReferenceLine
} from "recharts";

// ─── Constants & Metrics ──────────────────────────────────────────────────────

const MARQUEE_DATA = [
  "0.0% ATK Success Rate",
  "DeBERTa v3 Semantics",
  "< 13ms JWT Signing",
  "LLM Prompt Firewalls",
  "Reinforcement Learning Policy",
  "PPO Adapting Models",
  "Agent Stability Index (ASI)",
  "Zero Exfiltration Guarantee",
  "No PII Leakage",
  "Regex Prefilter Speed",
  "111ms Block Latency",
  "Multi-Agent Security",
];

const PHASE_DATA = [
  {
    phase: "Phase 1: Intent",
    title: "Dual-Model Filtering",
    icon: <Shield className="w-8 h-8 text-[#DC2626]" />,
    description: "Regex Prefilter & DeBERTa v3 intercept input prompts in <111ms. Accuracy jumps to 95.4% against obfuscation."
  },
  {
    phase: "Phase 2: Crypto",
    title: "Capability Tokens",
    icon: <Key className="w-8 h-8 text-[#EAB308]" />,
    description: "Multi-agent systems enforce cryptographic constraints. Forged tool interactions ('delete_file') are cryptographically blocked."
  },
  {
    phase: "Phase 3: Behavior",
    title: "Agent Stability Tracking",
    icon: <Activity className="w-8 h-8 text-[#DC2626]" />,
    description: "Continuous dialogue grading drops ASI index to 0.755 under sub-threshold malicious persistence. Triggers halt at <0.55."
  },
  {
    phase: "Phase 4: RL Def",
    title: "Self-Learning Sandbox",
    icon: <Zap className="w-8 h-8 text-[#EAB308]" />,
    description: "PPO algorithm continually tightens boundary thresholds (-0.05 step adjustments) eliminating zero-day evasion techniques."
  }
];

const ASR_DATA = [
  { name: "Undefended", rate: 80, fill: "rgba(255, 255, 255, 0.2)" },
  { name: "Rectitude Tier 1+2", rate: 2, fill: "#DC2626" },
];

const LATENCY_DATA = [
  { name: "Capability Issuance", ms: 13.77 },
  { name: "Injection Blocked", ms: 111 },
  { name: "Benign Processed", ms: 362 },
];

const ASI_DATA = [
  { turn: "T1 (Benign)", score: 1.0 },
  { turn: "T2 (Suspicious)", score: 0.755 },
  { turn: "T3 (Malicious)", score: 0.684 },
  { turn: "T4 (Threshold Break)", score: 0.54 },
];

// ─── Helper UI Components ─────────────────────────────────────────────────────

function GridOverlay() {
  return (
    <div
      className="pointer-events-none absolute inset-0 opacity-20"
      style={{
        backgroundImage:
          "linear-gradient(rgba(220,38,38,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(220,38,38,0.06) 1px, transparent 1px)",
        backgroundSize: "60px 60px",
      }}
    />
  );
}

// ─── Main Docs Page ───────────────────────────────────────────────────────────

export default function DocsPage() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Split marquee segments for infinite scrolling rows
  const limit = Math.ceil(MARQUEE_DATA.length / 3);
  const m1 = MARQUEE_DATA.slice(0, limit);
  const m2 = MARQUEE_DATA.slice(limit, limit * 2);
  const m3 = MARQUEE_DATA.slice(limit * 2);

  return (
    <main className="relative w-full min-h-screen bg-[#1A1A1A] selection:bg-[#DC2626] selection:text-white pb-32 overflow-x-hidden">
      {/* Navbar overlay */}
      <Navbar>
        <NavBody>
          <NavbarLogo />
          <NavItems
            items={[
              { name: "How It Works", link: "/#how-it-works" },
              { name: "Agents", link: "/agents" },
              { name: "Dashboard", link: "/dashboard" },
              { name: "Docs", link: "/docs" },
              { name: "Try Demo", link: "/chat" }
            ]}
          />
        </NavBody>
        <MobileNav visible={true}>
          <MobileNavHeader>
            <NavbarLogo />
            <MobileNavToggle isOpen={isMobileMenuOpen} onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} />
          </MobileNavHeader>
          <MobileNavMenu isOpen={isMobileMenuOpen} onClose={() => setIsMobileMenuOpen(false)}>
            <div className="flex flex-col gap-4 w-full">
              <a href="/#how-it-works" className="text-[#FFFFFF]">How It Works</a>
              <a href="/agents" className="text-[#FFFFFF]">Agents</a>
              <a href="/dashboard" className="text-[#FFFFFF]">Dashboard</a>
              <NavbarButton href="/chat" variant="gradient" className="w-full mt-4">Try Demo</NavbarButton>
            </div>
          </MobileNavMenu>
        </MobileNav>
      </Navbar>

      <GridOverlay />

      {/* ─── Hero Marquee Background Section ─── */}
      <section className="relative w-full overflow-hidden flex flex-col items-center z-10" style={{ paddingTop: '220px', paddingBottom: '80px' }}>
        <div className="absolute top-0 left-1/2 -translate-x-1/2 h-full w-[800px] rounded-full bg-[#DC2626] opacity-[0.03] blur-[150px] pointer-events-none" />

        <div className="text-center px-4 mb-16 select-none max-w-4xl relative z-20 mx-auto w-full flex flex-col items-center" style={{ marginLeft: 'auto', marginRight: 'auto' }}>

          <div className="font-display text-5xl sm:text-8xl md:text-8xl font-bold leading-tight text-white mb-8 flex flex-wrap justify-center gap-x-5 ">
            <TextEffect per="word" preset="blur" trigger={true}>The Hard</TextEffect>
            <TextEffect per="word" preset="blur" trigger={true} className="text-[#EAB308]">Metrics</TextEffect>
            <TextEffect per="word" preset="blur" trigger={true}>Behind</TextEffect>
            <TextEffect per="word" preset="blur" trigger={true} className="text-[#DC2626]">Rectitude.AI</TextEffect>
          </div>
        </div>

        {/* Marquee Badge Flow */}
        <div className="relative mx-auto w-full max-w-7xl overflow-hidden mt-6 mask-horizontal-gradient">
          <div className="absolute left-0 z-20 h-full w-24 bg-gradient-to-r from-[#1A1A1A] to-transparent pointer-events-none" />
          <div className="absolute right-0 z-20 h-full w-24 bg-gradient-to-l from-[#1A1A1A] to-transparent pointer-events-none" />

          <div className="flex flex-col gap-2 relative z-10 w-full transform">
            <Marquee className="[--duration:40s] [--gap:1rem]" repeat={4}>
              {m1.map((q) => <DocsBadge key={q}>{q}</DocsBadge>)}
            </Marquee>
            <Marquee className="[--duration:55s] [--gap:1.5rem]" repeat={4} reverse>
              {m2.map((q) => <DocsBadge key={q}>{q}</DocsBadge>)}
            </Marquee>
            <Marquee className="[--duration:45s] [--gap:1rem]" repeat={4}>
              {m3.map((q) => <DocsBadge key={q}>{q}</DocsBadge>)}
            </Marquee>
          </div>
        </div>
      </section>

      {/* ─── Uiverse Hover Cards: Phase Breakdown ─── */}
      <section className="relative z-20 w-full pt-40 pb-24 flex flex-col items-center justify-start min-h-[85vh] mx-auto overflow-hidden">
        <div className="w-full max-w-[1450px] mx-auto flex flex-col items-center px-6">
          <TextEffect
            per="char"
            preset="blur"
            trigger={true}
            className="text-2xl md:text-3xl font-bold text-white mb-8 text-center w-full"
          >
            Structural Phase Capabilities
          </TextEffect>
          <div className="h-[200px]" /> {/* Blank Padding Spacer */}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 w-full justify-items-center">
            {PHASE_DATA.map((card, i) => (
              <div key={i} className="docs-card mx-auto">
                <div className="docs-content">
                  {card.icon}
                  <div className="mt-2 flex flex-col items-center text-center">
                    <span className="text-xs font-mono text-[#DC2626] uppercase tracking-wider">{card.phase}</span>
                    <h3 className="text-xl font-bold text-white mt-1 mb-3 text-center">{card.title}</h3>
                    <p className="para text-sm leading-relaxed text-center">{card.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Spreaded Documentation: Section 01 ─── */}
      <section className="relative z-20 w-full py-64 flex flex-col items-center justify-start min-h-[85vh] mx-auto overflow-hidden bg-[#1A1A1A]">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-red-600/[0.02] blur-[180px] pointer-events-none" />

        <div className="w-full max-w-[1450px] mx-auto flex flex-col items-start px-6">
          <div className="text-xs font-mono uppercase tracking-[0.4em] text-red-500 mb-8 md:pl-[40%]">01. Architectural Rationale</div>
          <h2 className="text-5xl md:text-7xl font-bold text-white mb-16 max-w-5xl leading-tight">
            De-coupling Intent from Execution for Defense-in-Depth.
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-24 items-start w-full">
            <p className="text-2xl text-gray-400 font-serif leading-relaxed italic">
              "Unlike traditional regex filters, Rectitude.AI implements a 4-tier semantic barrier. We mitigate the risk of prompt injections by ensuring every instruction is validated against a pre-signed capability scope before touching the model weights."
            </p>
            <div className="bg-[#262626]/20 border border-white/5 p-12 rounded-[2rem] space-y-8">
              <div className="space-y-2">
                <h3 className="text-white font-bold uppercase tracking-widest text-sm">Strategy</h3>
                <p className="text-gray-500 text-sm leading-relaxed">
                  Interception happens at the head-end. By the time a prompt reaches the LLM, its intent has already been mathematically validated and scoped.
                </p>
              </div>
              <div className="space-y-2">
                <h3 className="text-white font-bold uppercase tracking-widest text-sm">Integrity</h3>
                <p className="text-gray-500 text-sm leading-relaxed">
                  Even a successful jailbreak cannot execute unauthorized tools, as every tool call requires a cryptographic HMAC signature issued only by the gateway.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Spreaded Documentation: Section 02 (Mathematical Hero) ─── */}
      <section className="relative z-20 w-full py-64 flex flex-col items-center justify-start min-h-[85vh] mx-auto overflow-hidden border-t border-b border-white/5">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[600px] bg-[#EAB308]/[0.01] blur-[150px] pointer-events-none" />

        <div className="w-full max-w-[1450px] mx-auto flex flex-col items-center px-6">
          <div className="text-xs font-mono uppercase tracking-[0.4em] text-red-500 mb-12">02. Mathematical Foundation</div>

          <div className="w-full flex flex-col items-center text-center space-y-20">
            <h2 className="text-5xl md:text-8xl font-bold text-white tracking-tighter">
              The ASI Equation
            </h2>

            <div className="text-3xl md:text-6xl font-serif italic text-white tracking-widest py-20 px-12 border-y border-white/10 w-full max-w-5xl">
              ASI = α · C + β · S<sub>sim</sub> + γ · V<sub>tool</sub>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-16 w-full max-w-5xl text-gray-500 font-mono text-xs uppercase tracking-[0.2em]">
              <div className="space-y-4">
                <div className="text-white border-b border-white/10 pb-2">Consistency (C)</div>
                <div>Semantic similarity to system role.</div>
              </div>
              <div className="space-y-4">
                <div className="text-white border-b border-white/10 pb-2">Similarity (S)</div>
                <div>Persona drift from agent centroids.</div>
              </div>
              <div className="space-y-4">
                <div className="text-white border-b border-white/10 pb-2">Variance (V)</div>
                <div>Frequency of high-risk tool calls.</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Spreaded Documentation: Section 03 (Benchmarks Header) ─── */}
      <section className="relative z-20 w-full pt-40 flex flex-col items-center justify-start mx-auto overflow-hidden">
        <div className="w-full max-w-[1450px] mx-auto flex flex-col items-start px-6">
          <div className="text-xs font-mono uppercase tracking-[0.4em] text-red-500 mb-8 md:pl-[40%]">03. Performance Metrics</div>
          <h2 className="text-5xl md:text-7xl font-bold text-white mb-8 leading-tight">
            Empirical Security Benchmarks
          </h2>
          <p className="text-xl text-gray-400 mb-20 max-w-3xl leading-relaxed">
            Through a combination of head-end Regex filtering and deep semantic DeBERTa verification, Rectitude.AI achieves 99.0% total attack coverage with an average total overhead of only 45ms.
          </p>
        </div>
      </section>

      {/* ─── Recharts Data Visualizations ─── */}
      <section className="relative z-20 w-full pt-40 pb-24 flex flex-col items-center justify-start min-h-[85vh] mx-auto overflow-hidden">
        <div className="w-full max-w-[1450px] mx-auto flex flex-col items-center px-6">
          <TextEffect
            per="char"
            preset="blur"
            trigger={true}
            className="text-2xl md:text-3xl font-bold text-white mb-8 text-center w-full"
          >
            Empirical Security Benchmarks
          </TextEffect>
          <div className="h-[200px]" /> {/* Blank Padding Spacer */}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 w-full">
            {/* ASR Chart */}
            <div className="bg-[#262626]/40 border border-white/5 rounded-2xl p-8 backdrop-blur-sm">
              <h3 className="text-xl font-bold text-white mb-1">Attack Success Rate (ASR)</h3>
              <p className="text-sm text-[#A1A1AA] mb-8">Base LLMs vs Rectitude.AI Prefix Layers</p>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={ASR_DATA} layout="vertical" margin={{ top: 0, right: 30, left: 20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255,255,255,0.1)" />
                    <XAxis type="number" stroke="#A1A1AA" tick={{ fill: '#A1A1AA' }} tickFormatter={(val) => `${val}%`} />
                    <YAxis dataKey="name" type="category" width={120} stroke="#A1A1AA" tick={{ fill: '#A1A1AA', fontSize: 12 }} />
                    <RechartsTooltip
                      cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                      contentStyle={{ backgroundColor: '#1A1A1A', borderColor: 'rgba(220,38,38,0.3)', borderRadius: '8px' }}
                    />
                    <Bar dataKey="rate" fill="#DC2626" radius={[0, 4, 4, 0]} barSize={32} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Latency Breakdown */}
            <div className="bg-[#262626]/40 border border-white/5 rounded-2xl p-8 backdrop-blur-sm">
              <h3 className="text-xl font-bold text-white mb-1">Processor Latency Budget</h3>
              <p className="text-sm text-[#A1A1AA] mb-8">Average Request Lifecycle Timing (ms)</p>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={LATENCY_DATA} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="name" stroke="#A1A1AA" tick={{ fill: '#A1A1AA', fontSize: 11 }} />
                    <YAxis stroke="#A1A1AA" tick={{ fill: '#A1A1AA' }} />
                    <RechartsTooltip
                      cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                      contentStyle={{ backgroundColor: '#1A1A1A', borderColor: 'rgba(220,38,38,0.3)', borderRadius: '8px' }}
                    />
                    <Bar dataKey="ms" fill="#EAB308" radius={[4, 4, 0, 0]} barSize={40} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* ASI Line Chart (Spans full width) */}
            <div className="bg-[#262626]/40 border border-white/5 rounded-2xl p-8 backdrop-blur-sm md:col-span-2">
              <h3 className="text-xl font-bold text-white mb-1">Agent Stability Index (ASI) Drift</h3>
              <p className="text-sm text-[#A1A1AA] mb-8">Simulating malicious persistence across multi-turn exchanges</p>
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={ASI_DATA} margin={{ top: 10, right: 30, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="turn" stroke="#A1A1AA" tick={{ fill: '#A1A1AA', fontSize: 12 }} />
                    <YAxis domain={[0, 1.2]} stroke="#A1A1AA" tick={{ fill: '#A1A1AA' }} />
                    <RechartsTooltip
                      contentStyle={{ backgroundColor: '#1A1A1A', borderColor: 'rgba(220,38,38,0.3)', borderRadius: '8px' }}
                      labelStyle={{ color: '#FFFFFF' }}
                      itemStyle={{ color: '#EAB308' }}
                    />
                    <ReferenceLine y={0.55} label={{ position: 'top', value: 'SYSTEM HALT THRESHOLD', fill: '#DC2626', fontSize: 10 }} stroke="#DC2626" strokeDasharray="3 3" />
                    <Line type="monotone" dataKey="score" stroke="#EAB308" strokeWidth={3} dot={{ r: 6, fill: '#1A1A1A', stroke: '#EAB308', strokeWidth: 2 }} activeDot={{ r: 8, fill: '#DC2626', stroke: '#DC2626' }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      </section>

      <FooterSection />
    </main>
  );
}
