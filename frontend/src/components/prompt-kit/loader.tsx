"use client";

import { cn } from "@/lib/utils";

interface LoaderProps {
  variant?: "dots" | "typing" | "shimmer" | "classic" | string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function Loader({ variant = "dots", size = "md", className }: LoaderProps) {
  const sizeClasses = {
    sm: "h-1.5 w-1.5",
    md: "h-2 w-2",
    lg: "h-3 w-3",
  };

  const dim = sizeClasses[size];

  if (variant === "typing") {
    return (
      <div className={cn("flex space-x-1.5", className)}>
        <div className={cn(dim, "bg-purple-500 rounded-full animate-bounce [animation-delay:-0.3s]")}></div>
        <div className={cn(dim, "bg-purple-500 rounded-full animate-bounce [animation-delay:-0.15s]")}></div>
        <div className={cn(dim, "bg-purple-500 rounded-full animate-bounce")}></div>
      </div>
    );
  }

  if (variant === "shimmer") {
    return (
      <div className={cn("relative w-24 h-4 bg-[rgba(123,63,228,0.1)] rounded overflow-hidden", className)}>
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[rgba(168,85,247,0.3)] to-transparent -translate-x-full animate-[shimmer_1.5s_infinite]" />
      </div>
    );
  }

  // default dots
  return (
    <div className={cn("flex items-center space-x-1.5", className)}>
      <div className={cn(dim, "bg-[#A855F7] rounded-full animate-pulse")}></div>
      <div className={cn(dim, "bg-[#A855F7] rounded-full animate-pulse opacity-70")}></div>
      <div className={cn(dim, "bg-[#A855F7] rounded-full animate-pulse opacity-40")}></div>
    </div>
  );
}
