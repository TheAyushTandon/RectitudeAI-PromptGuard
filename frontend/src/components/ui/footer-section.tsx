'use client';
import React from 'react';
import type { ComponentProps, ReactNode } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import Link from 'next/link';
import Image from 'next/image';

interface FooterLink {
  title: string;
  href: string;
}

interface FooterSection {
  label: string;
  links: FooterLink[];
}

const footerLinks: FooterSection[] = [
  {
    label: 'Pages',
    links: [
      { title: 'Demo Chat', href: '/chat' },
      { title: 'Agents', href: '/agents' },
      { title: 'Dashboard', href: '/dashboard' },
      { title: 'Settings', href: '/chat' },
    ],
  },
  {
    label: 'Socials',
    links: [
      { title: 'GitHub', href: 'https://github.com' },
      { title: 'Twitter', href: '#' },
      { title: 'LinkedIn', href: '#' },
      { title: 'Discord', href: '#' },
    ],
  },
  {
    label: 'Legal',
    links: [
      { title: 'Privacy Policy', href: '/privacy' },
      { title: 'Terms of Service', href: '/terms' },
      { title: 'Cookie Policy', href: '/cookie' },
    ],
  },
  {
    label: 'Register',
    links: [
      { title: 'Sign Up', href: '/signup' },
      { title: 'Login', href: '/login' },
      { title: 'Forgot Password', href: '/forgot-password' },
    ],
  },
];

export function FooterSection() {
  return (
    <footer className="w-full bg-[#0d0d0d] pt-24 pb-0 overflow-hidden font-sans relative">
      <div className="w-full max-w-7xl mx-auto px-6 lg:px-8 relative z-10">
        <div className="flex flex-col lg:flex-row gap-16 lg:gap-8 mb-24">
          
          {/* Brand section */}
          <AnimatedContainer className="flex flex-col gap-4 max-w-sm lg:w-1/3" delay={0}>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-white rounded-md flex items-center justify-center flex-shrink-0">
                <Image
                  src="/logo.svg"
                  alt="Logo"
                  width={20}
                  height={20}
                  className="opacity-90 brightness-0"
                />
              </div>
              <span className="font-bold text-lg text-white">Rectitude.AI</span>
            </div>
            <p className="text-[#a1a1aa] text-sm mt-3">
              © copyright Rectitude.AI {new Date().getFullYear()}. All rights reserved.
            </p>
          </AnimatedContainer>

          {/* Links columns */}
          <div className="flex-1 flex lg:justify-center">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-12 sm:gap-8 w-full max-w-3xl">
              {footerLinks.map((section, idx) => (
                <AnimatedContainer key={section.label} className="flex flex-col gap-6" delay={0.1 + idx * 0.1}>
                  <h3 className="font-semibold text-white text-base">
                    {section.label}
                  </h3>
                  <ul className="space-y-4">
                    {section.links.map((link) => (
                      <li key={link.title}>
                        <Link
                          href={link.href}
                          className="text-[15px] text-[#8e8e93] hover:text-white transition-colors duration-200"
                        >
                          {link.title}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </AnimatedContainer>
              ))}
            </div>
          </div>

        </div>
      </div>

      {/* Giant Background Text */}
      <div className="w-full relative flex justify-center items-end overflow-hidden pb-4 md:pb-8 pt-12">
        <h1 className="text-[16vw] md:text-[180px] xl:text-[240px] font-bold text-[#1a1a1a] leading-[0.75] tracking-tighter select-none whitespace-nowrap -mb-[2%]">
          Rectitude.AI
        </h1>
      </div>
    </footer>
  );
}

// ── Animated Container ──────────────────────────────────────────────────────
type ViewAnimationProps = {
  delay?: number;
  className?: ComponentProps<typeof motion.div>['className'];
  children: ReactNode;
};

function AnimatedContainer({ className, delay = 0.1, children }: ViewAnimationProps) {
  const shouldReduceMotion = useReducedMotion();

  if (shouldReduceMotion) {
    return <div className={className}>{children}</div>;
  }

  return (
    <motion.div
      initial={{ filter: 'blur(4px)', translateY: 12, opacity: 0 }}
      whileInView={{ filter: 'blur(0px)', translateY: 0, opacity: 1 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ delay, duration: 0.6, ease: "easeOut" }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
