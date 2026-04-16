"use client";

import React, { useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { format } from "date-fns";

export default function SecurityCharts({ stats, logs }: { stats: any; logs: any[] }) {
  // Memoize time series data for the ASI Risk chart
  const timeSeriesData = useMemo(() => {
    if (!logs || logs.length === 0) return [];
    
    // Reverse logs to show oldest on left, newest on right
    return [...logs].reverse().map((log) => ({
      time: format(new Date(log.timestamp), "HH:mm:ss"),
      risk: log.risk_score,
      action: log.action
    }));
  }, [logs]);

  // Transform stats into action distribution for PieChart
  const pieData = useMemo(() => {
    if (!stats || stats.total_requests === 0) {
      return [{ name: "No Data", value: 1, color: "#333" }];
    }
    const allowed = stats.total_requests - stats.blocked - stats.escalated;
    return [
      { name: "Cleared", value: allowed, color: "#10b981" }, // Emerald 500
      { name: "Flagged", value: stats.escalated, color: "#f59e0b" }, // Amber 500
      { name: "Intercepted", value: stats.blocked, color: "#ef4444" }, // Red 500
    ].filter(d => d.value > 0);
  }, [stats]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
      {/* ASI Risk Line Chart */}
      <div className="bg-white/[0.03] border border-white/10 backdrop-blur-md rounded-2xl p-6 h-80 flex flex-col items-center shadow-glass transition-all hover:bg-white/[0.05] group text-center relative overflow-hidden">
        <div className="mb-4 flex flex-col items-center">
          <h3 className="text-xs font-bold tracking-[0.3em] text-white/30 uppercase mb-1">ASI Risk Architecture</h3>
          <p className="text-xl font-bold font-sans text-white/90">Temporal Risk Drift</p>
        </div>
        <div className="flex-1 w-full min-h-0">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={timeSeriesData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
              <XAxis 
                dataKey="time" 
                fontSize={12} 
                fontWeight={500} 
                tickMargin={10} 
                axisLine={false}
                tickLine={false}
                tickFormatter={(val) => val.split(":")[2] ? `:${val.split(":")[2]}` : val}
              />
              <YAxis 
                fontSize={12} 
                fontWeight={500} 
                domain={[0, 1]} 
                tickCount={5}
                axisLine={false}
                tickLine={false}
              />
              <RechartsTooltip 
                contentStyle={{ 
                  backgroundColor: "rgba(20, 20, 20, 0.9)", 
                  border: "1px solid rgba(255, 255, 255, 0.1)",
                  borderRadius: "12px",
                  backdropFilter: "blur(10px)",
                  boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.5)"
                }}
                itemStyle={{ color: "#fff", fontSize: "12px" }}
                labelStyle={{ color: "#888", marginBottom: "4px", fontSize: "11px", fontWeight: "bold" }}
              />
              <Line 
                type="monotone" 
                dataKey="risk" 
                stroke="#f59e0b" 
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6, fill: "#f59e0b", stroke: "#000", strokeWidth: 2 }}
                isAnimationActive={true}
                animationDuration={1000}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Action Distribution Doughnut */}
      <div className="bg-white/[0.03] border border-white/10 backdrop-blur-md rounded-2xl p-6 h-80 flex flex-col items-center shadow-glass transition-all hover:bg-white/[0.05] group text-center relative overflow-hidden">
        <div className="mb-4 flex flex-col items-center">
          <h3 className="text-xs font-bold tracking-[0.3em] text-white/30 uppercase mb-1">Decision Engine</h3>
          <p className="text-xl font-bold font-sans text-white/90">Intervention Logic</p>
        </div>
        <div className="flex-1 w-full min-h-0 flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={65}
                outerRadius={85}
                paddingAngle={8}
                dataKey="value"
                stroke="none"
                isAnimationActive={true}
                animationDuration={800}
                cornerRadius={10}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} opacity={0.8} />
                ))}
              </Pie>
              <RechartsTooltip 
                 contentStyle={{ 
                  backgroundColor: "rgba(20, 20, 20, 0.9)", 
                  border: "1px solid rgba(255, 255, 255, 0.1)",
                  borderRadius: "12px",
                  backdropFilter: "blur(10px)"
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="flex justify-center gap-6 mt-4">
          {pieData.map(d => (
            <div key={d.name} className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full shadow-[0_0_8px_rgba(255,255,255,0.2)]" style={{ backgroundColor: d.color }}></span>
              <span className="text-[11px] font-bold text-white/50 uppercase tracking-tighter">{d.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
