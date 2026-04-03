"use client";
import Header from "@/components/layout/Header";

export default function AttackPanel() {
  return (
    <div className="flex-1 flex flex-col h-full bg-background-dark">
      <Header title="Attack Simulation Panel" subtitle="Launch automated adversarial stress-tests against the gateway" />
      <div className="flex-1 p-8 flex flex-col items-center justify-center opacity-30 select-none">
        <p className="font-mono text-xs uppercase tracking-[0.4em]">Red-Teaming Engine Skeleton - Awaiting attack_runner.py</p>
      </div>
    </div>
  );
}
