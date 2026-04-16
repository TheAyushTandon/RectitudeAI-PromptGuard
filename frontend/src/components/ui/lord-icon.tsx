"use client";

import React, { useRef, useEffect, useState } from "react";

interface LordIconProps {
  src: string;
  trigger?: string;
  colors?: string;
  delay?: string | number;
  size?: number;
  className?: string;
}

export const LordIcon = ({
  src,
  trigger = "hover",
  colors = "primary:#ffffff,secondary:#ffffff",
  delay,
  size = 32,
  className,
}: LordIconProps) => {
  const iconRef = useRef<any>(null);
  const [targetId, setTargetId] = useState<string | undefined>(undefined);

  useEffect(() => {
    // We use the native 'target' attribute of lord-icon to trigger
    // the animation from any parent element (like the entire sidebar tab).
    const parent = iconRef.current?.closest('a') || iconRef.current?.closest('button');
    if (parent) {
      if (!parent.id) {
        // Assign a unique ID if one doesn't exist
        parent.id = `lord-icon-target-${Math.random().toString(36).substring(2, 11)}`;
      }
      setTargetId(`#${parent.id}`);
    }
  }, []);

  return (
    <div className={className} style={{ width: size, height: size }}>
      {/* @ts-ignore */}
      <lord-icon
        ref={iconRef}
        src={src}
        trigger={trigger}
        colors={colors}
        delay={delay}
        target={targetId}
        style={{ width: size, height: size }}
      />
    </div>
  );
};
