"use client";

import { cn } from "@/lib/utils";
import { Markdown } from "./markdown";

export function Message({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("flex w-full", className)}>
      <div className="flex max-w-[100%] sm:max-w-[100%] gap-5">
        {children}
      </div>
    </div>
  );
}

export function MessageAvatar({ src, alt, fallback }: { src?: string; alt?: string; fallback?: string }) {
  return (
    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-[rgba(123,63,228,0.3)] bg-[rgba(123,63,228,0.1)] shadow-[0_0_12px_rgba(123,63,228,0.1)]">
      {src ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={src} alt={alt} className="h-5 w-5 brightness-0 invert" />
      ) : (
        <span className="text-xs font-semibold text-[#A855F7]">{fallback}</span>
      )}
    </div>
  );
}

export function MessageContent({
  children,
  markdown = false,
  className,
}: {
  children: React.ReactNode | string;
  markdown?: boolean;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-col gap-5 rounded-3xl text-white leading-relaxed", className)}>
      {markdown ? (
        <Markdown>{typeof children === "string" ? children : ""}</Markdown>
      ) : (
        typeof children === "string" ? <span>{children}</span> : children
      )}
    </div>
  );
}
