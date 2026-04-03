"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  ShieldCheck, 
  History, 
  Terminal, 
  Activity,
  ChevronRight,
  User
} from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const navItems = [
  { name: "Security Dashboard", icon: LayoutDashboard, href: "/dashboard" },
  { name: "Request Inspector", icon: ShieldCheck, href: "/requests" },
  { name: "Attack Simulation", icon: Activity, href: "/attack-panel" },
  { name: "Audit Logs", icon: History, href: "/audit" },
  { name: "API Playground", icon: Terminal, href: "/" },
  { name: "System Health", icon: Activity, href: "/system-health" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-[280px] h-screen bg-surface border-r border-muted/30 flex flex-col z-50 shrink-0">
      <div className="p-6 border-b border-muted/30 flex items-center justify-between">
        <div>
          <h1 className="text-primary font-bold text-xl tracking-wider text-glow uppercase">
            RectitudeAI
          </h1>
          <p className="text-[10px] text-muted font-mono tracking-widest mt-0.5">TACTICAL PRECISION</p>
        </div>
        <div 
          className="w-2.5 h-2.5 rounded-full bg-allowed shadow-neon-allowed animate-pulse" 
          title="SYSTEM: ENFORCING"
        />
      </div>

      <nav className="flex-1 overflow-y-auto py-6 px-3 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 px-4 py-3 rounded-none transition-all duration-200 border border-transparent",
                isActive 
                  ? "bg-primary/10 border-primary text-primary shadow-neon-primary relative" 
                  : "text-muted hover:bg-white/5 hover:border-muted/50 hover:text-text-main"
              )}
            >
              {isActive && (
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary shadow-neon-primary" />
              )}
              <item.icon className={cn(
                "w-5 h-5 transition-colors",
                isActive ? "text-primary text-glow" : "group-hover:text-primary"
              )} />
              <span className={cn(
                "text-[13px] font-bold uppercase tracking-wider",
                isActive && "text-glow"
              )}>
                {item.name}
              </span>
              {isActive && (
                <ChevronRight className="w-4 h-4 ml-auto animate-pulse" />
              )}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-muted/30 bg-background-dark/50">
        <div 
          className="flex items-center gap-3 p-2 border border-muted/20 hover:border-primary/30 transition-colors cursor-pointer group"
          onClick={() => {
             import('@/lib/api').then(module => module.logout());
          }}
          title="Click to logout"
        >
          <div className="w-9 h-9 bg-muted/20 flex items-center justify-center border border-muted/30 group-hover:border-primary/50 transition-colors">
            <User className="w-5 h-5 text-muted group-hover:text-primary transition-colors" />
          </div>
          <div className="min-w-0">
            <p className="text-[11px] font-mono text-text-main truncate uppercase">ADMIN_01</p>
            <p className="text-[9px] font-mono text-primary text-glow uppercase">SESSION: SECURE</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
