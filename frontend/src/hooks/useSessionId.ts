"use client";

import { useEffect, useRef } from "react";
import { useChatStore } from "@/store/chatStore";

/**
 * Ensures a stable session ID is generated exactly once on the client
 * (never on the server) and stored in the Zustand chat store.
 *
 * Use this hook at the top of any component that either displays or sends
 * the sessionId to the backend.
 */
export function useSessionId(): string {
  const sessionId = useChatStore((s) => s.sessionId);
  const initialized = useRef(false);

  useEffect(() => {
    if (!initialized.current && !sessionId) {
      initialized.current = true;
      const newId = `sess_${Math.random().toString(36).slice(2, 10)}`;
      useChatStore.setState({ sessionId: newId });
    }
  }, [sessionId]);

  return sessionId;
}
