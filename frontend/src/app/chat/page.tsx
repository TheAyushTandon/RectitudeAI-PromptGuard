"use client";

import React, { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import { FallingPattern } from "@/components/ui/falling-pattern";
import { PromptBox } from "@/components/ui/chatgpt-prompt-input";
import {
  Message,
  MessageAvatar,
  MessageContent,
} from "@/components/prompt-kit/message";

import { LordIcon } from "@/components/ui/lord-icon";
import { Sidebar, SidebarBody, SidebarLink } from "@/components/ui/sidebar";
import { motion, AnimatePresence } from "motion/react";
import { ThinkingBar } from "@/components/prompt-kit/thinking-bar";
import { 
  RefreshCw, 
  Database, 
  ShieldCheck, 
  Activity, 
  Cpu, 
  Lock, 
  Zap,
  Terminal,
  Settings,
  MessageSquare,
  Trash2
} from "lucide-react";

export default function ChatPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const [open, setOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("chat");
  const [currentModel, setCurrentModel] = useState<string>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("rectitude_selected_model") || "Select Model";
    }
    return "Select Model";
  });
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [isSecurityEnabled, setIsSecurityEnabled] = useState<boolean>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("rectitude_security_enabled");
      return saved !== null ? saved === "true" : true;
    }
    return true;
  });
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>("local_session");
  const [sessions, setSessions] = useState<any[]>([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  useEffect(() => {
    localStorage.setItem("rectitude_security_enabled", isSecurityEnabled.toString());
  }, [isSecurityEnabled]);

  useEffect(() => {
    if (currentModel && currentModel !== "Mistral 7B") {
      localStorage.setItem("rectitude_selected_model", currentModel);
    }
  }, [currentModel]);

  const fetchModels = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/v1/models");
      const data = await response.json();
      if (data.models && data.models.length > 0) {
        setAvailableModels(data.models);
        // Priority: Saved model > First available
        const savedModel = localStorage.getItem("rectitude_selected_model");
        if (savedModel && data.models.includes(savedModel)) {
          setCurrentModel(savedModel);
        } else if (currentModel === "Select Model" || !data.models.includes(currentModel)) {
          setCurrentModel(data.models[0]);
        }
      }
    } catch (err) {
      console.error("Failed to fetch models", err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSessions = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/v1/sessions");
      const data = await response.json();
      if (data.sessions) {
        setSessions(data.sessions);
      }
    } catch (err) {
      console.error("Failed to fetch sessions", err);
    }
  };

  const startNewChat = () => {
    const newId = `session_${Math.random().toString(36).substring(2, 9)}`;
    setSessionId(newId);
    setMessages([]);
    setIsHistoryOpen(false);
    setActiveTab("chat");
    // Optionally fetch sessions to refresh list (though new one won't have a title yet)
  };

  const deleteSession = async (e: React.MouseEvent, sid: string) => {
    e.stopPropagation(); // Don't trigger loadSession
    try {
      const response = await fetch(`http://127.0.0.1:8000/v1/history/${sid}`, {
        method: "DELETE"
      });
      if (response.ok) {
        setSessions(prev => prev.filter(s => s.session_id !== sid));
        if (sessionId === sid) {
          setMessages([]);
          setSessionId(`session_${Math.random().toString(36).substring(2, 9)}`);
        }
      }
    } catch (err) {
      console.error("Failed to delete session", err);
    }
  };

  const loadSession = async (sid: string) => {
    if (isLoading) return;
    setIsLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/v1/history/${sid}`);
      const data = await response.json();
      if (data.messages) {
        // Map backend history to frontend message format
        const formatted = data.messages.map((m: any) => ({
          role: m.role === "user" ? "user" : "ai",
          content: m.content,
          justify: m.role === "user" ? "justify-end" : "justify-start",
          avatar: m.role !== "user"
        }));
        setMessages(formatted);
        setSessionId(sid);
        setActiveTab("chat");
        setOpen(false); // Close sidebar on selection to focus on chat
      }
    } catch (err) {
      console.error("Failed to load session", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
    fetchSessions();
  }, []);

  const handleToggleModel = () => {
    const currentIndex = availableModels.indexOf(currentModel);
    const nextIndex = (currentIndex + 1) % availableModels.length;
    setCurrentModel(availableModels[nextIndex]);
  };

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const promptRef = useRef<any>(null);

  const links = [
    {
      label: "Dashboard",
      href: "/dashboard",
      icon: <LordIcon src="https://cdn.lordicon.com/wmwqvixz.json" trigger="hover" size={32} />,
    },
    {
      label: "AI Chat",
      href: "#",
      onClick: () => setActiveTab("chat"),
      icon: <LordIcon src="https://cdn.lordicon.com/hpivxauj.json" trigger="hover" size={32} />,
    },
    {
      label: "Chat History",
      href: "#",
      onClick: () => {
        setIsHistoryOpen(!isHistoryOpen);
        fetchSessions();
      },
      icon: (
        <div className="w-8 h-8 flex items-center justify-center">
          <svg
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
            width="28"
            height="28"
            fill="none"
            className="group-hover/sidebar:opacity-100 opacity-80"
          >
            <style>
              {`@keyframes slide-top-history{0%{transform:translateY(1px)}to{transform:translateY(-2px)}}`}
            </style>
            <path
              stroke="#FFFFFF"
              strokeLinecap="round"
              strokeWidth="1.5"
              d="M6 8.55v8.334c0 .92.768 1.667 1.714 1.667h8.572c.947 0 1.714-.746 1.714-1.667V8.551m-7 2.899h2"
            />
            <path
              fill="#FFFFFF"
              fillRule="evenodd"
              d="M4.087 5.45H3.87a.533.533 0 00-.533.532v.967c0 .295.238.533.533.533h16.26a.533.533 0 00.533-.533v-.967a.533.533 0 00-.533-.533H4.087z"
              clipRule="evenodd"
              className="group-hover/sidebar:[animation:slide-top-history_1s_cubic-bezier(.86,0,.07,1)_infinite_alternate-reverse_both]"
            />
          </svg>
        </div>
      ),
    },
    {
      label: "Agents",
      href: "#",
      onClick: () => {
        setMessages((prev) => [
          ...prev,
          {
            role: "ai",
            content: "### 🤖 Available Security Agents\nUse these commands to route your request through specialized security pipelines:\n\n*   **/general_utility** — Default reasoning & general security audit.\n*   **/hr_database** — Secure access to HR records & PII filtering.\n*   **/email_security** — Phishing detection and email content sanitization.\n*   **/finance_audit** — Transaction analysis and financial data protection.",
            justify: "justify-start",
            avatar: true,
          },
        ]);
      },
      icon: (
        <div className="w-8 h-8 flex items-center justify-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="28"
            height="28"
            fill="none"
            viewBox="0 0 24 24"
            className="group-hover/sidebar:opacity-100 opacity-80"
          >
            <style>
              {`
              @keyframes sliders {
                0% { transform: translateX(0px); }
                100% { transform: translateX(10px); }
              }
              @keyframes sliders-2 {
                0% { transform: translateX(0px); }
                100% { transform: translateX(-10px); }
              }
              `}
            </style>
            <path
              stroke="#FFFFFF"
              strokeLinecap="round"
              strokeWidth="1.5"
              d="M6 8.746h12M6 15.317h12"
            />
            <circle
              className="group-hover/sidebar:[animation:sliders_1.5s_cubic-bezier(0.86,0,0.07,1)_infinite_alternate_both]"
              cx="7.5"
              cy="8.746"
              r="1.5"
              fill="#FFFFFF"
              stroke="#FFFFFF"
              strokeWidth="1.5"
            />
            <circle
              className="group-hover/sidebar:[animation:sliders-2_1.5s_cubic-bezier(0.86,0,0.07,1)_infinite_alternate_both]"
              cx="16.5"
              cy="15.254"
              r="1.5"
              fill="#FFFFFF"
              stroke="#FFFFFF"
              strokeWidth="1.5"
            />
          </svg>
        </div>
      ),
    },
    {
      label: "Security",
      href: "/security",
      icon: (
        <div className="w-8 h-8 flex items-center justify-center">
          <svg
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
            width="28"
            height="28"
            fill="none"
            className="group-hover/sidebar:opacity-100 opacity-80"
          >
            <style>
              {`@keyframes check-animate{to{stroke-dashoffset: 0}}`}
            </style>
            <path
              stroke="#FFFFFF"
              strokeWidth="1.5"
              d="M5.9 8.053a2 2 0 011.507-1.938l4.683-1.192 4.517 1.184A2 2 0 0118.1 8.042v3.75a7 7 0 01-3.98 6.314l-.755.361a3 3 0 01-2.557.015l-.856-.398A7 7 0 015.9 11.736V8.053z"
            />
            <path
              stroke="#FFFFFF"
              strokeLinecap="round"
              strokeWidth="1.5"
              d="M9.215 12.052l1.822 1.805 3.748-3.714"
              className="group-hover/sidebar:[animation:check-animate_2s_infinite_cubic-bezier(.99,-.1,.01,1.02)]"
              strokeDashoffset="100"
              strokeDasharray="100"
            />
          </svg>
        </div>
      ),
    },
    {
      label: "Settings",
      href: "#",
      onClick: () => setActiveTab("settings"),
      icon: (
        <div className="w-8 h-8 flex items-center justify-center">
          <svg
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
            width="28"
            height="28"
            fill="none"
            className="group-hover/sidebar:opacity-100 opacity-80"
          >
            <style>
              {`@keyframes rotate-settings-v2{0%{transform:rotateZ(0)}to{transform:rotateZ(360deg)}}`}
            </style>
            <g
              className="group-hover/sidebar:[animation:rotate-settings-v2_3s_cubic-bezier(.7,-.03,.26,1.05)_both_infinite]"
              style={{
                transformOrigin: "center center",
              }}
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.5"
            >
              <path
                stroke="#FFFFFF"
                d="M5.262 15.329l.486.842a1.49 1.49 0 002.035.55 1.486 1.486 0 012.036.529c.128.216.197.463.2.714a1.493 1.493 0 001.493 1.536h.979a1.486 1.486 0 001.485-1.493 1.493 1.493 0 011.493-1.471c.252.002.498.071.714.2a1.493 1.493 0 002.036-.55l.521-.857a1.493 1.493 0 00-.542-2.036 1.493 1.493 0 010-2.586c.71-.41.952-1.318.543-2.028l-.493-.85a1.493 1.493 0 00-2.036-.579 1.479 1.479 0 01-2.029-.543 1.428 1.428 0 01-.2-.714c0-.825-.668-1.493-1.492-1.493h-.98c-.82 0-1.488.664-1.492 1.486a1.485 1.485 0 01-1.493 1.493 1.521 1.521 0 01-.714-.2 1.493 1.493 0 00-2.036.542l-.514.858a1.486 1.486 0 00.543 2.035 1.486 1.486 0 01.543 2.036c-.13.226-.317.413-.543.543a1.493 1.493 0 00-.543 2.028v.008z"
                clipRule="evenodd"
              />
              <path
                stroke="#FFFFFF"
                d="M12.044 10.147a1.853 1.853 0 100 3.706 1.853 1.853 0 000-3.706z"
              />
            </g>
          </svg>
        </div>
      ),
    },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (messages.length > 0) {
      scrollToBottom();
    }
  }, [messages]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const message = formData.get("message") as string;

    if (!message && !promptRef.current?.value) {
      return;
    }

    const content = message || promptRef.current?.value;
    let agentName = null;
    let promptText = content;

    if (content.startsWith("/")) {
      const match = content.match(/^\/(\w+)\s*(.*)/);
      if (match) {
        agentName = match[1];
        promptText = match[2] || content; // Use full content if just command
      }
    }

    if (content.trim()) {
      const userMessage = {
        role: "user",
        content: content,
        justify: "justify-end",
      };
      setMessages((prev) => [...prev, userMessage]);

      // Clear input using internal reset
      promptRef.current?.reset?.();
      setIsLoading(true);

      // Backend Call: AI Response
      try {
        const response = await fetch("http://127.0.0.1:8000/v1/agent/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: "demo_user",
            prompt: promptText,
            agent_name: agentName || "general_utility",
            session_id: sessionId,
            model: currentModel,
            is_security_enabled: isSecurityEnabled,
          }),
        });

        if (!response.ok) {
          throw new Error(`Backend response not ok: ${response.status}`);
        }

        const data = await response.json();
        
        setMessages((prev) => [
          ...prev,
          {
            role: "ai",
            content: data.response,
            justify: "justify-start",
            avatar: true,
          },
        ]);
        fetchSessions(); // Update titles
      } catch (error) {
        console.error("Failed to fetch AI response:", error);
        setMessages((prev) => [
          ...prev,
          {
            role: "ai",
            content: "Sorry, I encountered an error connecting to the Rectitude.AI security gateway.",
            justify: "justify-start",
            avatar: true,
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden font-sans relative">
      <Sidebar open={open} setOpen={setOpen}>
        <SidebarBody className="justify-between gap-10">
          <div className="flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
            <div className="mt-8 flex flex-col gap-2">
              {links.map((link, idx) => (
                <React.Fragment key={idx}>
                  <SidebarLink link={link} />
                  {link.label === "Chat History" && isHistoryOpen && open && (
                    <motion.div 
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      className="flex flex-col gap-3 pl-10 pr-4 mt-2 mb-4 overflow-hidden"
                    >
                      {/* New Chat Button */}
                      <button
                        onClick={startNewChat}
                        className="flex items-center justify-center gap-2 w-full p-2 rounded-md border border-neutral-800 text-neutral-400 hover:bg-white/5 hover:text-white transition-all text-xs font-medium group"
                      >
                        <span className="text-lg leading-none">+</span>
                        <span>New Chat</span>
                      </button>

                      <div className="flex flex-col gap-1 max-h-[300px] overflow-y-auto custom-scrollbar">
                        {sessions.length === 0 ? (
                          <span className="text-[10px] text-neutral-600 py-4 text-center italic font-mono">No historical records found.</span>
                        ) : (
                          sessions.slice().reverse().map((s) => (
                            <div key={s.session_id} className="relative group/card w-full">
                              <button
                                onClick={() => loadSession(s.session_id)}
                                className={cn(
                                  "text-[11px] text-center py-2 px-3 rounded-md border transition-all flex flex-col items-center gap-0.5 overflow-hidden w-full",
                                  sessionId === s.session_id 
                                    ? "text-white bg-white/10 border-white/20" 
                                    : "text-neutral-500 bg-transparent border-transparent hover:bg-white/5 hover:text-neutral-300"
                                )}
                              >
                                <span className="block w-full truncate font-medium">{s.title}</span>
                                <span className="block w-full truncate text-[8px] opacity-20 font-mono uppercase">ID: {s.session_id.substring(0, 8)}</span>
                              </button>
                              
                              {/* Delete Action Overlay */}
                              <button
                                onClick={(e) => deleteSession(e, s.session_id)}
                                className="absolute right-1 top-1/2 -translate-y-1/2 opacity-0 group-hover/card:opacity-100 p-1.5 hover:bg-red-500/10 hover:text-red-500 text-neutral-600 transition-all rounded-md"
                                title="Delete Session"
                              >
                                <Trash2 className="w-3 h-3" />
                              </button>
                            </div>
                          ))
                        )}
                      </div>
                    </motion.div>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>
          <div>
            <SidebarLink
              link={{
                label: "Profile",
                href: "/profile",
                icon: (
                  <LordIcon 
                    src="https://cdn.lordicon.com/kthelypq.json" 
                    trigger="hover" 
                    size={32} 
                  />
                ),
              }}
            />
          </div>
        </SidebarBody>

        <div className="flex-1 flex flex-col items-center justify-center relative h-full overflow-hidden w-full">
          {/* Dynamic Background Pattern */}
          <div className="absolute inset-0 z-0 pointer-events-none">
            <FallingPattern
              color="#A1A1AA"
              duration={500}
              className="h-full w-full opacity-40"
            />
          </div>

          <AnimatePresence mode="wait">
            {activeTab === "chat" ? (
              <motion.div 
                key="chat"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="flex flex-col items-center w-full h-full overflow-hidden"
              >
                {/* Messages Scroll Area / Empty State */}
                <div className="relative z-10 w-full flex-1 overflow-y-auto px-10 py-12 custom-scrollbar flex flex-col items-center">
                  <div className="w-full max-w-7xl flex flex-col min-h-full">
                    {messages.length === 0 ? (
                      <div className="flex flex-col items-center justify-center flex-1 animate-in fade-in duration-700">
                        <h1 className="text-4xl sm:text-5xl font-semibold text-center text-foreground dark:text-white tracking-tight">
                          How can I help you?
                        </h1>
                      </div>
                    ) : (
                      <div className="flex flex-col flex-1 gap-3 w-full">
                        <div className="flex-1" />
                        {messages.map((msg, i) => (
                          <Message
                            key={i}
                            className={cn(
                              "w-full flex",
                              msg.role === "user" ? "justify-end" : "justify-start"
                            )}
                          >
                            {msg.avatar && (
                              <MessageAvatar
                                src="/logo.svg"
                                alt="Rectitude.AI"
                                fallback="RA"
                              />
                            )}
                            <div
                              className={cn(
                                "flex flex-col",
                                msg.role === "user" ? "items-end" : "items-start"
                              )}
                            >
                              {msg.role === "ai" ? (
                                <motion.div
                                  initial={{ opacity: 0, y: 10 }}
                                  animate={{ opacity: 1, y: 0 }}
                                  transition={{ duration: 0.5, ease: "easeOut" }}
                                >
                                  <MessageContent
                                    markdown={msg.role === "ai"}
                                    className="text-lg max-w-2xl text-left !text-white !opacity-100"
                                  >
                                    {msg.content}
                                  </MessageContent>
                                </motion.div>
                              ) : (
                                <MessageContent
                                  markdown={false}
                                  className="bg-white/10 dark:bg-white/10 backdrop-blur-2xl border border-white/20 shadow-2xl !px-8 !py-3 text-lg font-medium max-w-[100%] !break-all !whitespace-pre-wrap text-left ml-auto"
                                >
                                  {msg.content}
                                </MessageContent>
                              )}
                            </div>
                          </Message>
                        ))}
                        <div ref={messagesEndRef} />
                      </div>
                    )}
                  </div>
                </div>

                {/* Input Area */}
                <div className="relative z-20 w-full flex flex-col items-center justify-center pb-12 pt-4 px-6 md:px-12">
                  <div className="w-full max-w-3xl">
                    <ThinkingBar 
                      isReasoning={isLoading} 
                      text="Thinking" 
                      className="max-w-3xl"
                    />
                    <form onSubmit={handleSubmit} className="w-full">
                      <PromptBox ref={promptRef} name="message" className="w-full" />
                    </form>
                    <p className="text-xs text-center text-muted-foreground mt-4 opacity-50">
                      Rectitude.AI can make mistakes. Verify important information.
                    </p>
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div 
                key="settings"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                className="flex flex-col items-center justify-center min-h-full w-full max-w-4xl mx-auto p-[10%] md:p-[15%] gap-12 z-15 overflow-y-auto"
              >
                <div className="text-center mb-4">
                  <h2 className="text-4xl font-bold text-white mb-2">Platform Settings</h2>
                  <p className="text-neutral-400">Configure your security gateway and model orchestration.</p>
                </div>

                {/* Model Selection List */}
                <div className="w-full space-y-4">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-[10px] font-mono text-[#DC2626] uppercase tracking-[0.4em] font-bold">Infrastructural Inventory</span>
                    <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10">
                       <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
                       <span className="text-[8px] text-white/50 font-mono tracking-widest uppercase">{availableModels.length} Models Found</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {availableModels.map((model) => (
                      <div 
                        key={model}
                        onClick={() => setCurrentModel(model)}
                        className={cn(
                          "p-6 cursor-pointer group transition-all rounded-xl relative overflow-hidden border",
                          currentModel === model 
                            ? "bg-white/[0.05] border-[#DC2626]/50 shadow-[0_0_20px_rgba(220,38,38,0.1)]" 
                            : "bg-white/[0.02] border-white/10 hover:border-white/20"
                        )}
                      >
                        <div className="relative z-10">
                          <div className="flex items-center justify-between mb-2">
                            <span className={cn(
                              "text-[8px] font-mono uppercase tracking-widest",
                              currentModel === model ? "text-[#DC2626]" : "text-neutral-500"
                            )}>
                              {currentModel === model ? "Active Sequence" : "Standby"}
                            </span>
                            {currentModel === model && (
                               <RefreshCw className="w-3 h-3 text-[#DC2626] animate-spin-slow" />
                            )}
                          </div>
                          <h4 className={cn(
                            "text-xl font-bold tracking-tight transition-colors",
                            currentModel === model ? "text-white" : "text-neutral-400 group-hover:text-neutral-200"
                          )}>
                            {model}
                          </h4>
                        </div>
                      </div>
                    ))}
                  </div>
                  <p className="text-[10px] text-neutral-600 font-medium text-center mt-4">Models discovered via local Ollama instance orchestrator.</p>
                </div>

                {/* Security Toggle */}
                <div className="w-full p-10 flex items-center justify-between bg-white/[0.02] backdrop-blur-[2px] border border-white/20 rounded-xl shadow-2xl relative">
                  <div className="absolute inset-0 bg-gradient-to-tr from-white/[0.03] to-transparent pointer-events-none" />
                  <div className="relative z-10 !pl-6 md:pl-10 flex-1 flex flex-col gap-1">
                    <h3 className="text-2xl font-bold text-white tracking-tight">Security Gateway</h3>
                    <p className="text-[10px] text-neutral-400 tracking-[0.2em] uppercase font-mono">5-Layer Protection Active</p>
                  </div>
                  <button 
                    onClick={() => setIsSecurityEnabled(!isSecurityEnabled)}
                    className={cn(
                      "h-10 w-18 rounded-full p-2 transition-all duration-500 relative flex items-center",
                      isSecurityEnabled ? "bg-[#DC2626] shadow-[0_0_30px_rgba(220,38,38,0.3)]" : "bg-white/10"
                    )}
                  >
                    <motion.div 
                      layout
                      transition={{ type: "spring", stiffness: 400, damping: 25 }}
                      className="h-6 w-6 rounded-full bg-white shadow-xl z-10"
                      style={{ marginLeft: isSecurityEnabled ? "auto" : "0" }}
                    />
                  </button>
                </div>

                <div className="mt-8 pt-8 w-full text-center">
                   <p className="text-[10px] text-red/20 uppercase font-mono tracking-[0.5em] font-medium">Rectitude.AI — Secure Orchestration Protocol</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </Sidebar>
    </div>
  );
}





