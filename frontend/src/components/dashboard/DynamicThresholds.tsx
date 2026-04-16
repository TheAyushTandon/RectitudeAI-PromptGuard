"use client";

import React, { useState, useEffect } from "react";
import { SlidersHorizontal, Shield, Zap, Sparkles, CheckCircle2 } from "lucide-react";
import ControlKnob from "../../components/ui/control-knob";

export default function DynamicThresholds({ settings }: { settings: any }) {
  const [localSettings, setLocalSettings] = useState(settings);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateSuccess, setUpdateSuccess] = useState(false);

  // Production-ready API Base
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  useEffect(() => {
    if (settings && !isUpdating) {
      setLocalSettings(settings);
    }
  }, [settings, isUpdating]);

  const handleKnobChange = async (key: string, value: number) => {
    if (!localSettings) return;
    
    setIsUpdating(true);
    const newSettings = {
      ...localSettings,
      [key]: value / 100 // Convert knob 0-100 to 0-1
    };
    
    setLocalSettings(newSettings);

    try {
      const res = await fetch(`${API_BASE}/v1/dashboard/settings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newSettings),
      });
      
      if (res.ok) {
        setUpdateSuccess(true);
        setTimeout(() => setUpdateSuccess(false), 2000);
      }
    } catch (e) {
      console.error("Failed to update settings", e);
    } finally {
      setIsUpdating(false);
    }
  };

  if (!localSettings) {
    return <div className="h-64 animate-pulse bg-white/5 rounded-2xl" />;
  }

  return (
    <div className="bg-white/[0.03] border border-white/10 backdrop-blur-md rounded-2xl p-6 shadow-glass h-full flex flex-col group">
      <div className="flex flex-col items-center text-center mb-6">
        <h3 className="text-xs font-bold tracking-[0.3em] text-white/30 uppercase mb-1">Neural Configuration</h3>
        <p className="text-xl font-bold font-sans text-white/90 mb-2">Dynamic Tuning</p>
        {updateSuccess && (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-widest">System Synced</span>
          </div>
        )}
      </div>

      <div className="flex-1 flex flex-col justify-around gap-8">
        <div className="grid grid-cols-2 gap-8">
          {/* ML Block Threshold */}
          <div className="flex flex-col items-center gap-4 p-4 transition-colors">
            <div className="text-[10px] font-bold text-red-400 uppercase tracking-widest">
                ML Intercept
            </div>
            <ControlKnob 
              size={100} 
              min={50} 
              max={100} 
              value={Math.round(localSettings.ml_block_threshold * 100)} 
              onChange={(v) => handleKnobChange("ml_block_threshold", v)}
              label="BLOCK"
            />
            <div className="text-center space-y-1">
               <p className="text-[10px] text-white/30 uppercase leading-none font-bold tracking-widest">Protection Floor</p>
               <p className="text-sm font-mono text-primary/80 font-bold">{localSettings.ml_block_threshold.toFixed(2)}</p>
            </div>
          </div>

          {/* ASI Alert Threshold */}
          <div className="flex flex-col items-center gap-4 p-4 transition-colors">
            <div className="text-[10px] font-bold text-amber-400 uppercase tracking-widest">
                ASI Sensitivity
            </div>
            <ControlKnob 
              size={100} 
              min={10} 
              max={100} 
              value={Math.round(localSettings.asi_alert_threshold * 100)} 
              onChange={(v) => handleKnobChange("asi_alert_threshold", v)}
              label="DRIFT"
            />
            <div className="text-center space-y-1">
               <p className="text-[10px] text-white/30 uppercase leading-none font-bold tracking-widest">Drift Trigger</p>
               <p className="text-sm font-mono text-primary/80 font-bold">{localSettings.asi_alert_threshold.toFixed(2)}</p>
            </div>
          </div>
        </div>

        {/* Pattern Logic Selection */}
        <div className="flex flex-col items-center gap-4 p-6 transition-colors mx-auto w-full">
            <div className="text-[10px] font-bold text-primary uppercase tracking-widest">
                Pattern Logic
            </div>
            <div className="flex items-center gap-12 w-full justify-center">
                <ControlKnob 
                  size={120} 
                  min={10} 
                  max={90} 
                  value={Math.round(localSettings.prefilter_escalate * 100)} 
                  onChange={(v) => handleKnobChange("prefilter_escalate", v)}
                  label="LOGIC"
                />
                <div className="space-y-3 max-w-[140px]">
                   <p className="text-[10px] text-white/40 uppercase leading-relaxed font-bold tracking-tight">
                      Escalates anomalous patterns to ML core if system confidence exceeds threshold.
                   </p>
                   <div className="bg-primary/10 border border-primary/20 rounded-lg px-3 py-1.5 inline-block shadow-[0_0_15px_rgba(var(--primary),0.1)]">
                      <span className="text-sm font-mono font-bold text-primary">{localSettings.prefilter_escalate.toFixed(2)}</span>
                   </div>
                </div>
            </div>
        </div>
      </div>
    </div>
  );
}
