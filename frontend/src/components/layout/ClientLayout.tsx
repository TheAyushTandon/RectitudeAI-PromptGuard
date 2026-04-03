"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Sidebar from "./Sidebar";
import { ShieldAlert } from "lucide-react";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem("rectitude_token");
      const isLoginPage = pathname === "/login";

      if (!token && !isLoginPage) {
        router.push("/login");
      } else if (token && isLoginPage) {
        router.push("/");
      } else {
        setIsAuthenticated(true);
      }
    };
    
    // Slight delay to prevent aggressive flashing during hydration
    const timer = setTimeout(checkAuth, 100);
    return () => clearTimeout(timer);
  }, [pathname, router]);

  if (isAuthenticated === null) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-background-dark h-full w-full">
        <ShieldAlert className="w-16 h-16 text-primary animate-pulse mb-6" />
        <div className="text-primary font-mono text-sm uppercase tracking-[0.3em]">
          Verifying Identity...
        </div>
      </div>
    );
  }

  const isLoginPage = pathname === "/login";

  return (
    <>
      {!isLoginPage && <Sidebar />}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        {children}
      </main>
    </>
  );
}
