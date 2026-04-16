import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";

export const metadata: Metadata = {
  title: "Rectitude.AI — LLM Security Gateway",
  description:
    "5-layer defense-in-depth security gateway protecting LLM infrastructure from prompt injections, social engineering, and data exfiltration.",
  keywords: ["LLM security", "prompt injection", "AI gateway", "defense in depth"],
  openGraph: {
    title: "Rectitude.AI — LLM Security Gateway",
    description: "Protect your LLM infrastructure from the inside out.",
    type: "website",
  },
};

import { Providers } from "@/components/providers";
import { Geist } from "next/font/google";
import { cn } from "@/utils-lib/utils";

const geist = Geist({subsets:['latin'],variable:'--font-sans'});


export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={cn("dark", "font-sans", geist.variable)}>
      <head>
        <link rel="icon" href="/logo.svg" type="image/svg+xml" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
        <link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=clash-display@600,700,500&display=swap" />
      </head>
      <body className="bg-[#1A1A1A] text-[#F0EBF8] font-sans antialiased">
        <Providers>{children}</Providers>
        <Script src="https://cdn.lordicon.com/lordicon.js" strategy="afterInteractive" />
      </body>
    </html>
  );
}
