"use client";

import { useEffect, useState, useRef, useLayoutEffect } from "react";
import { motion, useScroll, useTransform, useInView } from "motion/react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Image from "next/image";
import Link from "next/link";
import { ArrowRight, ExternalLink, ChevronRight, Check, X, Plug2, Building2, Bot, Diamond } from "lucide-react";
import { LordIcon } from "@/components/ui/lord-icon";
import { Navbar, NavBody, NavItems, NavbarLogo, NavbarButton, MobileNav, MobileNavHeader, MobileNavMenu, MobileNavToggle } from "@/components/ui/resizable-navbar";
import { ThreeDMarquee } from "@/components/ui/3d-marquee";
import { FooterSection } from "@/components/ui/footer-section";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

// ─── Floating Orbs ───────────────────────────────────────────────────────────
function FloatingOrbs() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="absolute top-1/4 left-1/4 h-96 w-96 rounded-full bg-[#DC2626] opacity-[0.07] blur-[120px] animate-float-slow" />
      <div className="absolute top-1/2 right-1/4 h-64 w-64 rounded-full bg-[#EAB308] opacity-[0.05] blur-[100px] animate-float" style={{ animationDelay: "2s" }} />
      <div className="absolute bottom-1/4 left-1/2 h-80 w-80 rounded-full bg-[#6366F1] opacity-[0.06] blur-[120px] animate-float-slow" style={{ animationDelay: "4s" }} />
    </div>
  );
}

// ─── Grid Overlay ─────────────────────────────────────────────────────────────
function GridOverlay() {
  return (
    <div
      className="pointer-events-none absolute inset-0 opacity-30"
      style={{
        backgroundImage:
          "linear-gradient(rgba(220,38,38,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(220,38,38,0.06) 1px, transparent 1px)",
        backgroundSize: "60px 60px",
      }}
    />
  );
}


// ─── Hero Content ─────────────────────────────────────────────────────────────
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.3,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20, filter: "blur(10px)" },
  visible: {
    opacity: 1,
    y: 0,
    filter: "blur(0px)",
    transition: {
      duration: 1.2,
      ease: [0.16, 1, 0.3, 1],
    },
  },
};

function HeroContent() {
  return (
    <motion.div 
      className="relative z-10 flex flex-col items-center text-center px-4 w-full gap-y-2" 
      style={{ paddingTop: '150px' }}
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Headline */}
      <motion.h1 
        className="font-display text-6xl sm:text-8xl md:text-[min(13vw,200px)] font-bold leading-[0.85] tracking-wide mb-32 w-full"
        variants={{
          visible: {
            transition: {
              staggerChildren: 0.12
            }
          }
        }}
      >
        {["PROTECT YOUR LLM", "INFRASTRUCTURE", "FROM THE INSIDE OUT."].map((line, i) => (
          <motion.span
            key={i}
            className="block h-full py-1"
            variants={itemVariants}
          >
            {i === 1 ? (
              <span className="gradient-text">{line}</span>
            ) : (
              line
            )}
          </motion.span>
        ))}
      </motion.h1>

      <div className="h-10" />

      {/* Subtext */}
      <motion.p
        className="max-w-4xl text-xl text-[#A1A1AA] leading-relaxed"
        variants={itemVariants}
      >
        Rectitude.AI wraps every LLM call in a 5-layer security sandwich — blocking prompt injections,
        social engineering, and data exfiltration before they ever reach your model.
      </motion.p>

      <div className="h-10" />

      {/* CTAs */}
      <motion.div
        className="flex flex-col sm:flex-row gap-8"
        variants={itemVariants}
      >
        <NavbarButton href="/chat" variant="uiverse" className="group">
          Try Live Demo
        </NavbarButton>
        <NavbarButton href="https://github.com" target="_blank" rel="noopener noreferrer" variant="uiverse" className="group">
          Read the Docs
        </NavbarButton>
      </motion.div>
    </motion.div>
  );
}

// ─── Security Layers Section ──────────────────────────────────────────────────
const LAYERS = [
  {
    number: "01",
    title: "Intent Security",
    subtitle: "Regex + ML Prefilter",
    description: "Dual-mode detection: lightning-fast regex catches known patterns, ML classifier catches novel attacks. Blocks in under 5ms.",
    iconSrc: "https://cdn.lordicon.com/oaflenfr.json",
    time: "<5ms",
    color: "#DC2626",
  },
  {
    number: "02",
    title: "Crypto Integrity",
    subtitle: "JWT Capability Tokens",
    description: "Every agent call requires a cryptographically signed capability token scoping exactly which tools can be invoked. Zero privilege escalation.",
    iconSrc: "https://cdn.lordicon.com/uwyclwiu.json",
    time: "0.4ms",
    color: "#B91C1C",
  },
  {
    number: "03",
    title: "Behavior Monitor",
    subtitle: "ASI Drift Detection",
    description: "Real-time Autonomous Safety Index tracks behavioral drift across multi-turn conversations. Alerts on persona hijacking attempts.",
    iconSrc: "https://cdn.lordicon.com/qhgfqgbe.json",
    time: "continuous",
    color: "#EAB308",
  },
  {
    number: "04",
    title: "Red Team Engine",
    subtitle: "RL Policy-Driven",
    description: "Reinforcement learning adversarial agent continuously probes for new attack vectors and updates defense policies automatically.",
    iconSrc: "https://cdn.lordicon.com/tqpfulob.json",
    time: "async",
    color: "#EF4444",
  },
  {
    number: "05",
    title: "Orchestration Layer",
    subtitle: "LangGraph Routing",
    description: "Intelligent multi-agent routing with output mediation — PII redacted, responses sanitized before delivery.",
    iconSrc: "https://cdn.lordicon.com/fmasbamy.json",
    time: "<200ms total",
    color: "#FCA5A5",
  },
];

function SecurityLayersSection() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Header
      gsap.from(".layers-header", {
        scrollTrigger: {
          trigger: ".layers-header",
          start: "top 85%",
        },
        y: 40,
        opacity: 0,
        duration: 1.5,
        ease: "power3.out"
      });

      // Cards
      const cards = gsap.utils.toArray(".security-card-anim");
      cards.forEach((card: any, i: number) => {
        const isLeft = i % 2 === 0;
        gsap.from(card, {
          scrollTrigger: {
            trigger: card,
            start: "top 90%",
          },
          x: isLeft ? -50 : 50,
          opacity: 0,
          duration: 1.8,
          ease: "expo.out"
        });
      });
    }, containerRef);
    return () => ctx.revert();
  }, []);

  return (
    <section id="architecture" ref={containerRef} className="relative mt-64 md:mt-[32rem] py-40 md:py-[22rem] px-4 flex flex-col items-center w-full overflow-hidden" style={{ marginTop: '200px' }}>
      <div className="w-full px-8 md:px-16 relative">
        <div className="layers-header text-center mb-40">
          <div style={{ marginBottom: "28px" }} className="text-[#FF4D4D] font-mono text-sm tracking-[0.3em] uppercase">
            Architecture
          </div>
          <h2 style={{ marginBottom: "32px" }} className="font-display text-5xl md:text-[100px] leading-[0.85] font-bold text-[#FFFFFF]">
            The 5-Layer <br />
            <span className="gradient-text">Security Sandwich</span>
          </h2>
          <p style={{ marginTop: "24px" }} className="text-center !text-center text-[#A1A1AA] text-xl w-full">
            Every prompt runs through all 5 layers in under 200ms total. <br className="hidden md:block" /> No shortcuts, no bypasses.
          </p>
        </div>

        {/* Central timeline line */}
        <div className="hidden md:block absolute left-1/2 top-72 bottom-0 w-px -ml-px bg-gradient-to-b from-transparent via-[rgba(220,38,38,0.2)] to-transparent" />

        <div className="space-y-12 md:space-y-0 mt-10 relative flex flex-col">
          {LAYERS.map((layer, i) => {
            const isLeft = i % 2 === 0;
            
            const cardContent = (
              <div className="security-card-anim w-full cursor-pointer hover:scale-[1.03] transition-transform duration-300">
                <div className="uiverse-card">
                  <div className="uiverse-card-controls">
                    <span className="uiverse-card-dot uiverse-card-dot-red"></span>
                    <span className="uiverse-card-dot uiverse-card-dot-yellow"></span>
                    <span className="uiverse-card-dot uiverse-card-dot-green"></span>
                    <span className="ml-auto font-mono text-xs text-white/30">Layer {layer.number}</span>
                  </div>
                  
                  <div className="flex items-start gap-6 mb-4">
                    <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl border border-white/10" style={{ background: `${layer.color}15` }}>
                      <LordIcon 
                        src={layer.iconSrc} 
                        trigger="hover" 
                        size={32} 
                        colors={`primary:#ffffff,secondary:${layer.color}`}
                      />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold">{layer.title}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs font-mono text-white/40">{layer.subtitle}</span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full border border-white/10 text-white/60 font-mono tracking-wider">{layer.time}</span>
                      </div>
                    </div>
                  </div>

                  <div className="card-description h-full">
                    <p className="text-base text-white/60 leading-relaxed">{layer.description}</p>
                  </div>
                </div>
              </div>
            );

            return (
              <div key={layer.number} className="w-full flex flex-col md:flex-row items-center md:justify-between py-20 md:py-36">
                {/* Left side */}
                <div className="w-full md:w-5/12 flex justify-end order-1 md:order-1" style={isLeft ? { paddingLeft: '120px' } : {}}>
                  {isLeft && cardContent}
                </div>
                
                {/* Center dot */}
                <div className="hidden md:flex w-2/12 justify-center relative items-center z-10 order-2">
                  <div className="w-6 h-6 rounded-full border border-white/10 flex items-center justify-center bg-[#1A1A1A]">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: layer.color }} />
                  </div>
                </div>
                
                {/* Right side */}
                <div className="w-full md:w-5/12 flex justify-start order-3 md:order-3 mt-12 md:mt-0" style={!isLeft ? { paddingRight: '120px' } : {}}>
                  {!isLeft && cardContent}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

// ─── Why Rectitude Section ────────────────────────────────────────────────────
const THREATS = [
  { 
    metric: "Prompt Injection", 
    legacy: "Static blocklists easily bypassed", 
    rectitude: "Blocked at Tier 1 in <5ms", 
    tier: "Tier 1" 
  },
  { 
    metric: "Persona Hijacking", 
    legacy: "Generic pattern matching", 
    rectitude: "Regex + ML dual detection", 
    tier: "Tier 1-2" 
  },
  { 
    metric: "Data Exfiltration", 
    legacy: "Post-hoc alert logs only", 
    rectitude: "Output mediator redacts PII", 
    tier: "Tier 5" 
  },
  { 
    metric: "Multi-Turn Jailbreaks", 
    legacy: "Stateless per-request logic", 
    rectitude: "ASI behavioral monitoring", 
    tier: "Tier 3" 
  },
  { 
    metric: "Tool Privilege Abuse", 
    legacy: "Exploitable all-access tokens", 
    rectitude: "JWT Capability Tokens", 
    tier: "Tier 2" 
  },
  { 
    metric: "SQL Injection", 
    legacy: "Generic gateway WAF dependency", 
    rectitude: "Agent output sandboxing", 
    tier: "Tier 5" 
  },
];

function ComparisonAndMarqueeSection() {
  const containerRef = useRef(null);
  const isInView = useInView(containerRef, { once: true, amount: 0.2 });

  return (
    <section id="why-rectitude" ref={containerRef} className="relative mt-64 md:mt-[32rem] py-40 md:py-[22rem] px-6 bg-[#1A1A1A] flex flex-col items-center w-full" style={{ marginTop: '300px' }}>
      {/* --- Part 1: Comparison --- */}
      <div className="w-full flex flex-col items-center mx-auto">
        {/* Header Text */}
        <motion.div
          className="text-center mb-20 md:mb-32 flex flex-col items-center w-full relative z-30"
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
        >
          <div style={{ marginBottom: "28px" }} className="text-[#FF4D4D] font-mono text-xs tracking-[0.4em] uppercase">
            Comparison
          </div>
          <h2 style={{ marginBottom: "32px" }} className="font-display text-5xl md:text-[90px] leading-[1] font-bold text-white max-w-5xl">
            Traditional vs <span className="gradient-text">Rectitude.AI</span>
          </h2>
          <p style={{ marginTop: "24px" }} className="text-center !text-center text-lg text-[#A1A1AA] font-medium w-full max-w-4xl">
            While static gateways rely on legacy pattern matching, <br className="hidden md:block" /> Rectitude uses multi-tier intelligence to secure the entire LLM lifecycle.
          </p>
        </motion.div>

        {/* Decorative Spacer */}
        <div className="h-40 md:h-80 w-full" />

        {/* Zig-Zag Focal Divergent Branching Network */}
        <div className="relative w-full max-w-7xl mx-auto px-4 md:px-0 mb-80">
          
          <div className="relative flex flex-col space-y-64 md:space-y-[400px]">
            {THREATS.map((t, i) => (
              <div 
                key={i} 
                className={`relative w-full flex flex-col items-center transition-all duration-1000`}
                style={{
                  transform: `translateX(${i % 2 === 0 ? '-10%' : '10%'})`
                }}
              >
                
                {/* Central Metric Root Node (Raw Text) */}
                <motion.div 
                   className="relative z-30"
                   initial={{ opacity: 0, scale: 0.8, y: 20 }}
                   animate={isInView ? { opacity: 1, scale: 1, y: 0 } : {}}
                   transition={{ duration: 0.8, delay: i * 0.1, ease: "easeOut" }}
                >
                  <div className="relative group/root">
                    <span className="text-white font-black text-2xl md:text-5xl tracking-[0.6em] uppercase whitespace-nowrap drop-shadow-[0_10px_30px_rgba(0,0,0,0.5)] bg-clip-text">
                      {t.metric}
                    </span>
                  </div>
                </motion.div>

                {/* Branching Connections (Flow-based SVG) */}
                <div className="w-full h-40 md:h-60 -mt-4 relative z-0">
                  <motion.svg className="w-full h-full overflow-visible" viewBox="0 0 1000 100" preserveAspectRatio="none">
                    {/* Left Branch */}
                    <motion.path 
                      d="M 500 0 C 500 50, 250 50, 250 100"
                      fill="none" 
                      stroke="rgba(239, 68, 68, 0.4)" 
                      strokeWidth="2" 
                      initial={{ pathLength: 0, opacity: 0 }}
                      whileInView={{ pathLength: 1, opacity: 1 }}
                      viewport={{ once: true, margin: "-100px" }}
                      transition={{ duration: 0.8, delay: 0.2, ease: "easeInOut" }}
                    />
                    {/* Right Branch */}
                    <motion.path 
                      d="M 500 0 C 500 50, 750 50, 750 100"
                      fill="none" 
                      stroke="rgba(16, 185, 129, 0.5)" 
                      strokeWidth="2"
                      initial={{ pathLength: 0, opacity: 0 }}
                      whileInView={{ pathLength: 1, opacity: 1 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.8, delay: 0.2, ease: "easeInOut" }}
                    />
                  </motion.svg>
                </div>

                {/* Minimalist Color-Coded Text Nodes */}
                <div className="grid grid-cols-2 w-full gap-0 relative z-30 -mt-4">
                  {/* Legacy Text (Left) */}
                  <motion.div 
                    className="flex justify-center pr-[5%]"
                    initial={{ opacity: 0, x: -40 }}
                    animate={isInView ? { opacity: 1, x: 0 } : {}}
                    transition={{ duration: 0.8, delay: i * 0.1 + 0.3 }}
                  >
                    <p className="text-red-500/60 text-base md:text-xl font-medium leading-relaxed italic text-right whitespace-nowrap">
                      "{t.legacy}"
                    </p>
                  </motion.div>

                  {/* Rectitude Text (Right) */}
                  <motion.div 
                    className="flex justify-center pl-[5%]"
                    initial={{ opacity: 0, x: 40 }}
                    animate={isInView ? { opacity: 1, x: 0 } : {}}
                    transition={{ duration: 0.8, delay: i * 0.1 + 0.3 }}
                  >
                    <p className="text-emerald-400 text-xl md:text-3xl font-bold leading-tight tracking-tight text-left whitespace-nowrap">
                      {t.rectitude}
                    </p>
                  </motion.div>
                </div>

              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}


// ─── How It Works Section ─────────────────────────────────────────────────────
const STEPS = [
  {
    step: "01",
    title: "Request Arrives",
    items: ["JWT verified", "Rate limit checked", "User identified", "Session tracked"],
  },
  {
    step: "02",
    title: "Security Sandwich Runs",
    items: ["5 layers execute", "<200ms total", "Risk scored 0.0–1.0", "ASI updated"],
  },
  {
    step: "03",
    title: "Safe Response Delivered",
    items: ["Output mediated", "PII redacted", "Audit log written", "Delivered safely"],
  },
];

function HowItWorksSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.1 });

  return (
    <section id="how-it-works" ref={ref} className="relative mt-64 md:mt-[32rem] py-40 md:py-[22rem] px-10 md:px-20 flex flex-col items-center w-full" style={{ marginTop: '300px' }}>
      <div className="w-full max-w-7xl mx-auto">
        <motion.div
          className="text-center mb-24 relative z-30"
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
        >
          <p style={{ marginBottom: "28px" }} className="text-sm font-mono text-[#DC2626] tracking-widest uppercase">Flow</p>
          <h2 style={{ marginBottom: "32px" }} className="font-display text-5xl md:text-[100px] leading-[0.85] font-bold text-[#FFFFFF]">
            How It <span className="gradient-text">Works</span>
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-16 mt-20">
          {STEPS.map((step, i) => (
            <motion.div
              key={step.step}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              whileHover={{ scale: 1.05, zIndex: 50 }}
              transition={{ duration: 1.0, delay: i * 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="relative min-w-0 cursor-pointer z-30"
            >
              <div className="uiverse-card h-full">
                <div className="uiverse-card-controls">
                  <span className="uiverse-card-dot uiverse-card-dot-red"></span>
                  <span className="uiverse-card-dot uiverse-card-dot-yellow"></span>
                  <span className="uiverse-card-dot uiverse-card-dot-green"></span>
                  <span className="ml-auto font-mono text-xs text-white/30">Process Stage</span>
                </div>

                <div className="flex items-baseline gap-4 mb-6">
                  <span className="font-mono text-4xl font-black text-red-500/20">{step.step}</span>
                  <h3 className="font-semibold text-[#FFFFFF] text-2xl">{step.title}</h3>
                </div>

                <div className="card-description">
                  <ul className="space-y-4">
                    {step.items.map((item) => (
                      <li key={item} className="flex items-center gap-3 text-base text-[#A1A1AA]">
                        <div className="h-1.5 w-1.5 rounded-full bg-red-500/40" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              
              {i < STEPS.length - 1 && (
                <div className="hidden md:block absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 bg-[#1A1A1A] p-2 rounded-full border border-white/5 z-20">
                  <ArrowRight className="h-4 w-4 text-white/20" />
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── Use Cases Section ────────────────────────────────────────────────────────
const USE_CASES = [
  {
    icon: <Plug2 className="h-10 w-10 text-[#DC2626]" />,
    title: "LLM API Providers",
    description: "Wrap your API endpoints with 5-layer defense before serving any user prompt. Drop-in middleware for OpenAI-compatible APIs.",
    features: ["Prompt injection shield", "Output sanitization", "Rate limiting"],
  },
  {
    icon: <Building2 className="h-10 w-10 text-[#DC2626]" />,
    title: "Enterprise Deployments",
    description: "Protect internal chatbots from data leakage and insider prompt attacks. Audit every interaction for compliance.",
    features: ["PII redaction", "Audit logging", "Role-based agent scoping"],
  },
  {
    icon: <Bot className="h-10 w-10 text-[#DC2626]" />,
    title: "AI Agents & Copilots",
    description: "Multi-agent systems need token-scoped tool authority separation. Prevent agents from stepping outside their permission boundary.",
    features: ["JWT capability tokens", "Tool scope enforcement", "ASI monitoring"],
  },
];

function UseCasesSection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.1 });

  return (
    <section id="use-cases" ref={ref} className="relative mt-64 md:mt-[32rem] py-40 md:py-[22rem] pb-32 md:pb-48 px-10 md:px-20 bg-[#1A1A1A] flex flex-col items-center w-full">
      <div className="w-full max-w-7xl mx-auto">
        <motion.div
          className="text-center mb-24 relative z-30"
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
        >
          <p style={{ marginBottom: "28px" }} className="text-sm font-mono text-[#DC2626] tracking-widest uppercase">Use Cases</p>
          <h2 style={{ marginBottom: "32px" }} className="font-display text-5xl md:text-[90px] leading-[1] font-bold text-[#FFFFFF]">
            Built for Every <span className="gradient-text">LLM Stack</span>
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-16 mt-20">
          {USE_CASES.map((uc, i) => (
            <motion.div
              key={uc.title}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              whileHover={{ scale: 1.05, zIndex: 50 }}
              transition={{ duration: 1.0, delay: i * 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="group relative min-w-0 cursor-pointer z-30"
            >
              <div className="uiverse-card h-full">
                <div className="uiverse-card-controls">
                  <span className="uiverse-card-dot uiverse-card-dot-red"></span>
              <span className="uiverse-card-dot uiverse-card-dot-yellow"></span>
                  <span className="uiverse-card-dot uiverse-card-dot-green"></span>
                  <span className="ml-auto font-mono text-xs text-white/30">Solution Scope</span>
                </div>

                <div className="mb-6 opacity-80 group-hover:opacity-100 transition-all">{uc.icon}</div>
                <h3 className="font-semibold text-[#FFFFFF] text-2xl mb-2">{uc.title}</h3>
                
                <div className="card-description">
                  <p className="text-base text-[#A1A1AA] leading-relaxed mb-6">{uc.description}</p>
                  <ul className="space-y-3 border-t border-white/5 pt-6">
                    {uc.features.map((f) => (
                      <li key={f} className="flex items-center gap-3 text-sm text-[#EAB308]">
                        <div className="h-1.5 w-1.5 rounded-full bg-red-500" />
                        {f}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── Transition Spacer ────────────────────────────────────────────────────────
function TransitionSpacer() {
  return (
    <div className="h-[10vh] md:h-[20vh] w-full bg-[#1A1A1A]" />
  );
}

// ─── Stats Bar ────────────────────────────────────────────────────────────────
function StatsBar() {
  return (
    <section className="py-44 px-4 border-y border-[rgba(220,38,38,0.1)] flex flex-col items-center w-full">
      <div className="w-full">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-16 text-center">
          {[
            { value: "99.2%", label: "Attack Block Rate", sublabel: "Across all threat types" },
            { value: "<5ms", label: "Tier-1 Response", sublabel: "Regex prefilter speed" },
            { value: "5", label: "Specialized Agents", sublabel: "HR, Email, Code, Finance, General" },
            { value: "Zero", label: "Data Retained", sublabel: "Stateless per-request processing" },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <div className="text-3xl md:text-4xl font-bold font-mono gradient-text mb-2">{stat.value}</div>
              <div className="text-sm font-semibold text-[#FFFFFF] mb-1">{stat.label}</div>
              <div className="text-xs text-[#A1A1AA]">{stat.sublabel}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── Main Landing Page ────────────────────────────────────────────────────────
export default function LandingPage() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <main className="relative min-h-screen bg-[#1A1A1A] selection:bg-[#DC2626] selection:text-white overflow-x-hidden">
      <FloatingOrbs />
      <GridOverlay />
      <Navbar>
        <NavBody>
          <NavbarLogo />
          <NavItems 
            items={[
              { name: "How It Works", link: "#how-it-works" },
              { name: "Agents", link: "#architecture" },
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
              <Link href="#how-it-works" className="text-[#FFFFFF]">How It Works</Link>
              <Link href="#architecture" onClick={() => setIsMobileMenuOpen(false)} className="text-[#FFFFFF]">Agents</Link>
              <Link href="/dashboard" className="text-[#FFFFFF]">Dashboard</Link>
              <NavbarButton href="/chat" variant="gradient" className="w-full mt-4">Try Demo </NavbarButton>
            </div>
          </MobileNavMenu>
        </MobileNav>
      </Navbar>


      {/* Hero + Mask Reveal */}
      <section className="relative flex flex-col items-center overflow-hidden pt-[30rem] md:pt-[35rem] pb-48 min-h-screen">
        <div className="absolute inset-0 hero-radial" />
        <HeroContent />
      </section>

      
      <StatsBar />
      <SecurityLayersSection />
      <ComparisonAndMarqueeSection />
      <HowItWorksSection />
      <TransitionSpacer />
      <UseCasesSection />
      <TransitionSpacer />
      <FooterSection />
    </main>
  );
}
