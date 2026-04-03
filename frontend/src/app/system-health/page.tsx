"use client";

import { useEffect, useState } from "react";
import Header from "@/components/layout/Header";
import api from "@/lib/api";
import { 
  Activity, 
  Cpu, 
  Database, 
  Globe, 
  Router, 
  ShieldCheck, 
  Zap, 
  Settings,
  PlusSquare,
  History,
  Info,
  RefreshCw
} from "lucide-react";

// Mapping icon types from backend to Lucide icons
const IconMap: Record<string, any> = {
  Router: Router,
  Cpu: Cpu,
  Database: Database,
  Zap: Zap,
  ShieldCheck: ShieldCheck,
  Activity: Activity
};

export default function SystemHealth() {
  const [healthData, setHealthData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchHealth = async () => {
    setLoading(true);
    try {
      const response = await api.get("/health");
      setHealthData(response.data);
    } catch (error) {
      console.error("Failed to fetch health data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex-1 flex flex-col h-full bg-background-dark">
      <Header 
        title="System Health" 
        subtitle="Real-time infrastructure monitoring across core neural services and edge security"
        showActionButton
        onAction={fetchHealth}
        actionLoading={loading}
      />

      <main className="flex-1 overflow-y-auto p-8 font-display">
        <div className="max-w-7xl mx-auto space-y-8">
          
          {/* Metrics Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
             {[
               { label: "Uptime (24h)", val: "99.98%", trend: "+0.02%", col: "allowed" },
               { label: "Global Latency", val: healthData?.infrastructure?.[0]?.latency || "--", trend: "+4ms", col: "blocked" },
               { label: "API Version", val: healthData?.version || "v0.0.0", trend: "STABLE", col: "primary" },
               { label: "Success Rate", val: "100%", trend: "MAX", col: "allowed" },
             ].map((m, i) => (
              <div key={i} className="p-5 bg-surface border border-muted/20 hover:border-muted/50 transition-colors">
                <p className="text-[10px] font-black text-muted uppercase tracking-widest mb-2">{m.label}</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-black text-text-main">{m.val}</span>
                  <span className={`text-[10px] font-bold ${m.col === 'allowed' ? 'text-allowed' : m.col === 'blocked' ? 'text-blocked' : 'text-primary'}`}>{m.trend}</span>
                </div>
              </div>
             ))}
          </div>

          {/* Infrastructure Table */}
          <section>
             <h3 className="text-sm font-bold uppercase tracking-[0.2em] text-muted mb-4 flex items-center gap-2">
                <PlusSquare className="w-4 h-4 text-primary" />
                Core Infrastructure
             </h3>
             <div className="border border-muted/20 bg-surface overflow-hidden">
                <table className="w-full text-left">
                  <thead className="bg-[#0c0e14] border-b border-muted/20">
                    <tr className="text-[10px] font-black text-muted uppercase tracking-widest">
                      <th className="px-6 py-4">Service Node</th>
                      <th className="px-6 py-4">Status</th>
                      <th className="px-6 py-4">Latency</th>
                      <th className="px-6 py-4">Region</th>
                      <th className="px-6 py-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-muted/10 font-mono text-xs">
                    {loading && !healthData ? (
                      <tr>
                        <td colSpan={5} className="px-6 py-12 text-center text-muted animate-pulse uppercase tracking-[0.3em]">
                           Establishing telemetry uplink...
                        </td>
                      </tr>
                    ) : (
                      healthData?.infrastructure?.map((node: any, i: number) => {
                        const Icon = IconMap[node.icon_type] || Activity;
                        return (
                          <tr key={i} className="hover:bg-white/5 transition-colors">
                            <td className="px-6 py-4">
                              <div className="flex items-center gap-3">
                                <Icon className="w-4 h-4 text-primary" />
                                <span className="font-bold text-text-main uppercase tracking-tight">{node.name}</span>
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div className={`inline-flex items-center gap-2 px-2 py-0.5 border text-[9px] font-black ${
                                node.status === 'ACTIVE' ? 'border-allowed text-allowed bg-allowed/10' : 'border-escalated text-escalated bg-escalated/10'
                              }`}>
                                <div className={`w-1 h-1 rounded-full ${node.status === 'ACTIVE' ? 'bg-allowed animate-pulse' : 'bg-escalated'}`} />
                                {node.status}
                              </div>
                            </td>
                            <td className="px-6 py-4 text-muted">{node.latency}</td>
                            <td className="px-6 py-4 text-muted">{node.region}</td>
                            <td className="px-6 py-4 text-right">
                              <button className="text-muted hover:text-primary transition-colors">
                                <Settings className="w-4 h-4" />
                              </button>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
             </div>
          </section>

          {/* Incident History */}
           <section>
             <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-bold uppercase tracking-[0.2em] text-muted flex items-center gap-2">
                  <History className="w-4 h-4 text-primary" />
                  Incident History (7d)
                </h3>
                <div className="flex gap-4 text-[9px] font-black uppercase tracking-widest text-muted">
                  <div className="flex items-center gap-1"><div className="w-2 h-2 bg-allowed" /> Healthy</div>
                  <div className="flex items-center gap-1"><div className="w-2 h-2 bg-escalated" /> Degradation</div>
                  <div className="flex items-center gap-1"><div className="w-2 h-2 bg-blocked" /> Outage</div>
                </div>
             </div>
             <div className="p-6 border border-muted/20 bg-surface">
                <div className="flex justify-between items-center mb-4">
                   <span className="text-[11px] font-bold text-text-main uppercase">Neural Engine Cluster</span>
                   <span className="font-mono text-[10px] text-primary/60 uppercase">SYSTEM_STATE: STABLE</span>
                </div>
                <div className="flex gap-1 h-10">
                   {Array.from({length: 30}).map((_, i) => (
                      <div key={i} className={`flex-1 ${i === 22 ? 'bg-blocked/40 border border-blocked/20' : i === 15 ? 'bg-escalated/40 border border-escalated/20' : 'bg-allowed/40 border border-allowed/20'}`} />
                   ))}
                </div>
             </div>
          </section>

        </div>
      </main>
    </div>
  );
}
