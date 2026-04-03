"use client";

import { useState } from "react";
import { performLogin } from "@/lib/api";
import { ShieldCheck, ShieldAlert, Lock, User, TerminalSquare } from "lucide-react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await performLogin(username, password);
      // Success, redirect to dashboard or playground
      router.push("/");
    } catch (err: any) {
      setError("AUTHENTICATION FAILED: Invalid credentials or session timeout.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center bg-background-dark relative terminal-bg h-full w-full">
      {/* Tactical Grid Background */}
      <div className="absolute inset-0 pointer-events-none opacity-20 border-[1px] border-primary/20" />
      
      <div className="w-full max-w-md p-8 glass-card border border-primary/30 shadow-neon-primary/20 relative animate-in fade-in zoom-in-95 duration-500">
        <div className="absolute -top-4 -left-4 w-8 h-8 border-t-2 border-l-2 border-primary" />
        <div className="absolute -bottom-4 -right-4 w-8 h-8 border-b-2 border-r-2 border-primary" />

        <div className="flex flex-col items-center mb-8">
          <TerminalSquare className="w-12 h-12 text-primary mb-4 animate-pulse opacity-80" />
          <h1 className="text-3xl font-black text-primary uppercase tracking-widest text-glow">RectitudeAI</h1>
          <p className="text-[10px] text-muted font-mono tracking-[0.4em] mt-2">RESTRICTED ACCESS TERMINAL</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div className="space-y-2">
            <label className="text-[10px] font-bold text-muted uppercase tracking-widest flex items-center gap-2">
              <User className="w-3.5 h-3.5" />
              Operator ID
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-surface/50 border border-muted/30 focus:border-primary px-4 py-3 text-sm font-mono text-text-main outline-none transition-colors"
              placeholder="admin"
              required
            />
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-bold text-muted uppercase tracking-widest flex items-center gap-2">
              <Lock className="w-3.5 h-3.5" />
              Passcode
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-surface/50 border border-muted/30 focus:border-primary px-4 py-3 text-sm font-mono text-text-main outline-none transition-colors"
              placeholder="••••••••"
              required
            />
          </div>

          {error && (
            <div className="p-3 bg-blocked/10 border-l-2 border-blocked flex items-start gap-3 animate-in fade-in slide-in-from-top-2">
              <ShieldAlert className="w-4 h-4 text-blocked shrink-0 mt-0.5" />
              <p className="text-[10px] uppercase font-mono text-blocked leading-relaxed tracking-wider">
                {error}
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary/10 hover:bg-primary/20 border border-primary text-primary font-bold uppercase tracking-widest py-3 text-sm transition-all duration-300 shadow-neon-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                INITIATING HANDSHAKE...
              </>
            ) : (
              <>
                <ShieldCheck className="w-4 h-4" />
                AUTHENTICATE
              </>
            )}
          </button>
        </form>

        <div className="mt-8 text-center border-t border-muted/20 pt-4">
          <p className="text-[9px] text-muted font-mono uppercase tracking-widest opacity-50">
            Unauthorized access is strictly prohibited. Logging enabled.
          </p>
        </div>
      </div>
    </div>
  );
}
