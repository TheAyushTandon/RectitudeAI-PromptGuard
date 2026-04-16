"use client";

import { cn } from "../../lib/utils";
import React, { useState, useEffect, useCallback, useRef } from "react";
import { motion, useMotionValue, useTransform, useSpring, useMotionValueEvent } from "framer-motion";

interface ControlKnobProps {
  size?: number;
  min?: number;
  max?: number;
  value?: number;
  onChange?: (value: number) => void;
  label?: string;
}

export default function ControlKnob({
  size = 160,
  min = 0,
  max = 100,
  value = 37,
  onChange,
  label = "LEVEL"
}: ControlKnobProps) {
  // --- CONFIGURATION ---
  const MIN_DEG = -135;
  const MAX_DEG = 135;
  const TOTAL_TICKS = 40;
  const DEGREES_PER_TICK = (MAX_DEG - MIN_DEG) / TOTAL_TICKS;

  // --- STATE & PHYSICS ---
  const [isDragging, setIsDragging] = useState(false);
  
  // Calculate initial degree from provided value
  const initialDeg = ((value - min) / (max - min)) * (MAX_DEG - MIN_DEG) + MIN_DEG;
  
  // 1. RAW ANGLE: The exact, unsnapped position of mouse
  const rawRotation = useMotionValue(initialDeg);

  // 2. SNAPPED ANGLE: The position of the mechanical knob
  const snappedRotation = useMotionValue(initialDeg);
  
  // 3. SMOOTHED PHYSICS: Adds weight/inertia
  const smoothRotation = useSpring(snappedRotation, { 
    stiffness: 400, 
    damping: 35, 
    mass: 0.8
  });

  // Sync internal state with external value prop
  useEffect(() => {
    if (!isDragging) {
      const deg = ((value - min) / (max - min)) * (MAX_DEG - MIN_DEG) + MIN_DEG;
      rawRotation.set(deg);
      snappedRotation.set(deg);
    }
  }, [value, min, max, isDragging]);

  // --- TRANSFORMATIONS ---
  // Display Value (0-100) based on the PHYSICAL knob position
  const displayValue = useTransform(smoothRotation, [MIN_DEG, MAX_DEG], [min, max]);

  // Light Opacity based on the RAW mouse position (Instant Feedback)
  const lightOpacity = useTransform(rawRotation, [MIN_DEG, MAX_DEG], [0.05, 0.4]);

  // --- INTERACTION LOGIC ---
  const knobRef = useRef<HTMLDivElement>(null);

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    setIsDragging(true);
    document.body.style.cursor = "grabbing";
    document.body.style.userSelect = "none";
  }, []);

  useEffect(() => {
    if (!isDragging) return;

    const handlePointerMove = (e: PointerEvent) => {
      if (!knobRef.current) return;

      const rect = knobRef.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      const x = e.clientX - centerX;
      const y = e.clientY - centerY;
     
      let rads = Math.atan2(y, x);
      let degs = rads * (180 / Math.PI) + 90;

      if (degs > 180) degs -= 360;

      if (degs < MIN_DEG && degs > -180) degs = MIN_DEG;
      if (degs > MAX_DEG) degs = MAX_DEG;

      rawRotation.set(degs);

      const snap = Math.round(degs / DEGREES_PER_TICK) * DEGREES_PER_TICK;
      snappedRotation.set(snap);

      // Trigger onChange with calculated value
      if (onChange) {
        const calculatedValue = ((snap - MIN_DEG) / (MAX_DEG - MIN_DEG)) * (max - min) + min;
        onChange(Math.round(calculatedValue));
      }
    };

    const handlePointerUp = () => {
      setIsDragging(false);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };

    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", handlePointerUp);

    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);
    };
  }, [isDragging, rawRotation, snappedRotation, DEGREES_PER_TICK, max, min, onChange]);

  const ticks = Array.from({ length: TOTAL_TICKS + 1 });

  return (
    <div className="relative flex flex-col items-center justify-center pointer-events-auto" style={{ width: size, height: size }}>
      
      {/* Background Glow */}
      <motion.div 
          className="absolute inset-0 bg-primary/20 rounded-full blur-2xl pointer-events-none" 
          style={{ opacity: lightOpacity }}
      />

      <div className="relative w-full h-full select-none">
        
        {/* --- TICK MARKS RING --- */}
        <div className="absolute inset-0 pointer-events-none">
        {ticks.map((_, i) => {
            const angle = (i / TOTAL_TICKS) * (MAX_DEG - MIN_DEG) + MIN_DEG;
            return (
            <div
                key={i}
                className="absolute top-0 left-1/2 w-0.5 h-full -translate-x-1/2"
                style={{ transform: `rotate(${angle}deg)` }}
            >
                <TickMark currentRotation={smoothRotation} angle={angle} />
            </div>
            );
        })}
        </div>

        {/* --- THE KNOB --- */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" style={{ width: size * 0.6, height: size * 0.6 }}>
            <motion.div
                ref={knobRef}
                className={cn(
                  "relative w-full h-full rounded-full touch-none z-20 shadow-2xl",
                  isDragging ? "cursor-grabbing" : "cursor-grab"
                )}
                style={{ rotate: smoothRotation }}
                onPointerDown={handlePointerDown}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
            >
                {/* Knob Body */}
                <div className="w-full h-full rounded-full bg-neutral-900 shadow-[0_10px_30px_rgba(0,0,0,0.8),inset_0_1px_1px_rgba(255,255,255,0.1)] border border-neutral-800 flex items-center justify-center relative overflow-hidden">
                    <div className="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_30%_30%,rgba(255,255,255,0.1),transparent_50%),conic-gradient(from_0deg,transparent_0deg,#000_360deg)]" />
                    
                    {/* Top Cap */}
                    <div className="relative w-4/5 h-4/5 rounded-full bg-neutral-950 shadow-[inset_0_2px_5px_rgba(0,0,0,1)] border border-neutral-800/50 flex flex-col items-center justify-center">
                        <motion.div 
                            className="absolute top-2 w-1 h-3 bg-primary rounded-full shadow-[0_0_8px_rgba(var(--primary),0.5)]" 
                            style={{ 
                              boxShadow: useTransform(rawRotation, (r) => `0 0 ${Math.max(4, (r + 135) / 15)}px #f97316`)
                            }} 
                        />
                        <span className="font-mono text-[8px] text-neutral-500 tracking-widest mt-2">{label}</span>
                    </div>
                </div>
            </motion.div>
        </div>
      </div>
    </div>
  );
}

function TickMark({ currentRotation, angle }: { currentRotation: any, angle: number }) {
    const opacity = useTransform(currentRotation, (r: number) => {
        return r >= angle ? 1 : 0.15;
    });
    const color = useTransform(currentRotation, (r: number) => {
        return r >= angle ? "#f97316" : "#404040";
    });
    const boxShadow = useTransform(currentRotation, (r: number) => {
        return r >= angle ? "0 0 4px rgba(249, 115, 22, 0.4)" : "none";
    });

    return (
        <motion.div 
            style={{ backgroundColor: color, opacity, boxShadow }}
            className="w-full h-1.5 rounded-full transition-colors duration-75"
        />
    );
}
