"use client"

import { TextShimmer } from "@/components/ui/text-shimmer"
import { cn } from "@/utils-lib/utils"
import { ChevronRight } from "lucide-react"
import { motion, AnimatePresence } from "motion/react"

export type ThinkingBarProps = {
  className?: string
  text?: string
  onStop?: () => void
  stopLabel?: string
  onClick?: () => void
  isReasoning?: boolean
}

export function ThinkingBar({
  className,
  text = "Thinking",
  onStop,
  stopLabel = "Answer now",
  onClick,
  isReasoning = false
}: ThinkingBarProps) {
  return (
    <AnimatePresence>
      {isReasoning && (
        <motion.div
           initial={{ opacity: 0, y: 10 }}
           animate={{ opacity: 1, y: 0 }}
           exit={{ opacity: 0, scale: 0.95 }}
           className={cn("flex w-full items-center justify-between py-4", className)}
        >
          {onClick ? (
            <button
              type="button"
              onClick={onClick}
              className="flex items-center gap-1 text-sm transition-opacity hover:opacity-80"
            >
              <TextShimmer className="font-medium text-white/50">{text}</TextShimmer>
            </button>
          ) : (
            <TextShimmer className="cursor-default font-medium text-white/50 tracking-wider text-xs uppercase">{text}</TextShimmer>
          )}
          {onStop ? (
            <button
              onClick={onStop}
              type="button"
              className="text-muted-foreground hover:text-white border-muted-foreground/30 hover:border-white border-b border-dotted text-[10px] uppercase font-mono tracking-widest transition-colors"
            >
              {stopLabel}
            </button>
          ) : null}
        </motion.div>
      )}
    </AnimatePresence>
  )
}
