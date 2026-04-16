"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { ReactLenis } from "lenis/react";
import { AnimatePresence, motion } from "motion/react";
import { usePathname, useSearchParams } from "next/navigation";
import React, { useState, useEffect, Suspense } from "react";
import NProgress from "nprogress";
import "nprogress/nprogress.css";

// Configure NProgress
NProgress.configure({ showSpinner: false, speed: 400, minimum: 0.1 });

function NavigationHandler() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    NProgress.done();
    return () => {
      NProgress.start();
    };
  }, [pathname, searchParams]);

  return null;
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,
        refetchOnWindowFocus: false,
      },
    },
  }));

  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return <div className="bg-[#1A1A1A]">{children}</div>;

  return (
    <QueryClientProvider client={queryClient}>
      <Suspense fallback={null}>
        <NavigationHandler />
      </Suspense>
      <ReactLenis root options={{ lerp: 0.1, duration: 1.5, smoothWheel: true }}>
        <AnimatePresence mode="wait">
          <motion.div
            key={pathname}
            initial={{ opacity: 0, scale: 0.995 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.005 }}
            transition={{
              duration: 0.4,
              ease: [0.23, 1, 0.32, 1] as any, // Fluid cubic-bezier
            }}
            className="min-h-screen flex flex-col"
          >
            {children}
          </motion.div>
        </AnimatePresence>
      </ReactLenis>
      {process.env.NODE_ENV === 'development' && <ReactQueryDevtools initialIsOpen={false} />}
      <style jsx global>{`
        #nprogress .bar {
          background: #7C3AED !important;
          height: 3px !important;
          box-shadow: 0 0 10px #7C3AED, 0 0 5px #7C3AED;
        }
        ::selection {
          background: rgba(124, 58, 237, 0.3);
          color: white;
        }
      `}</style>
    </QueryClientProvider>
  );
}
