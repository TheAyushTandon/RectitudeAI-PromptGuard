"use client";
import { cn } from "../../lib/utils";
import { IconMenu2, IconX } from "@tabler/icons-react";
import {
  motion,
  AnimatePresence,
  useScroll,
  useMotionValueEvent,
} from "motion/react";

import React, { useRef, useState } from "react";


interface NavbarProps {
  children: React.ReactNode;
  className?: string;
}

interface NavBodyProps {
  children: React.ReactNode;
  className?: string;
  visible?: boolean;
}

interface NavItemsProps {
  items: {
    name: string;
    link: string;
  }[];
  className?: string;
  onItemClick?: () => void;
}

interface MobileNavProps {
  children: React.ReactNode;
  className?: string;
  visible?: boolean;
}

interface MobileNavHeaderProps {
  children: React.ReactNode;
  className?: string;
}

interface MobileNavMenuProps {
  children: React.ReactNode;
  className?: string;
  isOpen: boolean;
  onClose: () => void;
}

export const Navbar = ({ children, className }: NavbarProps) => {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollY } = useScroll();
  const [visible, setVisible] = useState<boolean>(false);

  useMotionValueEvent(scrollY, "change", (latest) => {
    if (latest > 100) {
      setVisible(true);
    } else {
      setVisible(false);
    }
  });

  return (
    <motion.div
      ref={ref}
      // Floating fixed at the top
      className={cn("fixed inset-x-0 top-8 z-50 w-full flex justify-center", className)}
    >
      {React.Children.map(children, (child) =>
        React.isValidElement(child)
          ? React.cloneElement(
            child as React.ReactElement<{ visible?: boolean }>,
            { visible },
          )
          : child,
      )}
    </motion.div>
  );
};

export const NavBody = ({ children, className, visible }: NavBodyProps) => {
  return (
    <motion.div
      animate={{
        backdropFilter: visible ? "blur(10px)" : "none",
        boxShadow: visible
          ? "0 0 24px rgba(34, 42, 53, 0.06), 0 1px 1px rgba(10, 10, 10, 0.05), 0 0 0 1px rgba(34, 42, 53, 0.04), 0 0 4px rgba(34, 42, 53, 0.08), 0 16px 68px rgba(47, 48, 55, 0.05), 0 1px 0 rgba(255, 255, 255, 0.1) inset"
          : "none",
        width: visible ? "65%" : "100%",
        y: visible ? 20 : 0,
        paddingLeft: visible ? "80px" : "40px",
        paddingRight: visible ? "80px" : "40px",
        paddingTop: visible ? "20px" : "40px",
        paddingBottom: visible ? "20px" : "40px",
      }}
      transition={{
        type: "spring",
        stiffness: 200,
        damping: 50,
      }}
      style={{
        minWidth: "800px",
        paddingLeft: "80px",
        paddingRight: "80px",
      }}
      className={cn(
        "relative z-[60] mx-auto hidden w-full max-w-[1200px] flex-row items-center justify-between self-start rounded-full bg-transparent py-10 lg:flex dark:bg-transparent",
        visible && "bg-[rgba(10, 10, 10,0.85)] border border-[rgba(220,38,38,0.3)] dark:bg-neutral-950/80",
        className,
      )}
    >
      {children}
    </motion.div>
  );
};

export const NavItems = ({ items, className, onItemClick }: NavItemsProps) => {
  const [hovered, setHovered] = useState<number | null>(null);

  return (
    <motion.div
      onMouseLeave={() => setHovered(null)}
      className={cn(
        "hidden flex-1 flex-row items-center justify-center gap-12 text-sm font-medium text-[#A1A1AA] transition duration-200 lg:flex",
        className,
      )}
    >
      {items.map((item, idx) => (
        <a
          onMouseEnter={() => setHovered(idx)}
          onClick={onItemClick}
          className="relative px-8 py-3 hover:text-black hover:-translate-y-0.5 transition-all duration-300 whitespace-nowrap"
          key={`link-${idx}`}
          href={item.link}
        >
          {hovered === idx && (
            <motion.div
              layoutId="hovered-nav"
              className="absolute inset-x-[-10px] inset-y-[-4px] h-[calc(100%+8px)] w-[calc(100%+20px)] rounded-full bg-white shadow-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            />
          )}
          <span className="relative z-20 font-bold">{item.name}</span>
        </a>
      ))}
    </motion.div>
  );
};

export const MobileNav = ({ children, className, visible }: MobileNavProps) => {
  return (
    <motion.div
      animate={{
        backdropFilter: visible ? "blur(10px)" : "none",
        boxShadow: visible
          ? "0 0 24px rgba(34, 42, 53, 0.06), 0 1px 1px rgba(10, 10, 10, 0.05), 0 0 0 1px rgba(34, 42, 53, 0.04), 0 0 4px rgba(34, 42, 53, 0.08), 0 16px 68px rgba(47, 48, 55, 0.05), 0 1px 0 rgba(255, 255, 255, 0.1) inset"
          : "none",
        width: visible ? "90%" : "100%",
        paddingRight: visible ? "12px" : "0px",
        paddingLeft: visible ? "12px" : "0px",
        borderRadius: visible ? "4px" : "2rem",
        y: visible ? 20 : 0,
      }}
      transition={{
        type: "spring",
        stiffness: 200,
        damping: 50,
      }}
      className={cn(
        "relative z-50 mx-auto flex w-full max-w-[calc(100vw-2rem)] flex-col items-center justify-between bg-transparent px-0 py-2 lg:hidden",
        visible && "bg-[rgba(10, 10, 10,0.85)] border border-[rgba(220,38,38,0.3)] dark:bg-neutral-950/80",
        className,
      )}
    >
      {children}
    </motion.div>
  );
};

export const MobileNavHeader = ({
  children,
  className,
}: MobileNavHeaderProps) => {
  return (
    <div
      className={cn(
        "flex w-full flex-row items-center justify-between px-12",
        className,
      )}
    >
      {children}
    </div>
  );
};

export const MobileNavMenu = ({
  children,
  className,
  isOpen,
  onClose,
}: MobileNavMenuProps) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className={cn(
            "absolute inset-x-0 top-16 z-50 flex w-full flex-col items-start justify-start gap-4 rounded-lg bg-[#1A1A1A] border border-[rgba(220,38,38,0.3)] px-4 py-8 shadow-2xl backdrop-blur-xl dark:bg-neutral-950",
            className,
          )}
        >
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export const MobileNavToggle = ({
  isOpen,
  onClick,
}: {
  isOpen: boolean;
  onClick: () => void;
}) => {
  return isOpen ? (
    <IconX className="text-[#FFFFFF] dark:text-white" onClick={onClick} />
  ) : (
    <IconMenu2 className="text-[#FFFFFF] dark:text-white" onClick={onClick} />
  );
};

export const NavbarLogo = () => {
  return (
    <a
      href="#"
      className="relative z-20 mr-8 ml-6 flex flex-shrink-0 items-center gap-2 px-2 py-1 text-base font-normal text-white"
    >
      <img
        src="/logo.svg"
        alt="logo"
        width={20}
        height={20}
        className="brightness-0 invert"
      />
      <span className="font-black font-sans text-white dark:text-white tracking-wider text-lg">Rectitude.AI</span>
    </a>
  );
};

export const NavbarButton = ({
  href,
  as: Tag = "a",
  children,
  className,
  variant = "primary",
  ...props
}: {
  href?: string;
  as?: React.ElementType;
  children: React.ReactNode;
  className?: string;
  variant?: "primary" | "secondary" | "dark" | "gradient" | "uiverse";
} & (
    | React.ComponentPropsWithoutRef<"a">
    | React.ComponentPropsWithoutRef<"button">
  )) => {
  const baseStyles =
    "rounded-full button text-white text-sm font-bold relative cursor-pointer transition-all duration-300 inline-flex items-center justify-center gap-4 whitespace-nowrap text-center";

  const isUiverse = variant === "uiverse";

  const variantStyles = {
    primary:
      "px-6 py-3 bg-white text-black shadow-[0_0_24px_rgba(34,_42,_53,_0.06)] hover:bg-[#F5F5F5] hover:-translate-y-1",
    secondary: "px-6 py-3 bg-transparent shadow-none dark:text-white text-[#FFFFFF] font-medium border border-[rgba(220,38,38,0.3)] hover:border-[#DC2626] hover:bg-[rgba(220,38,38,0.05)] hover:-translate-y-1",
    dark: "px-6 py-3 bg-black text-white hover:bg-white hover:text-black hover:-translate-y-1",
    gradient:
      "px-6 py-3 bg-gradient-to-r from-[#DC2626] to-[#EAB308] text-white hover:brightness-110 hover:shadow-lg hover:shadow-[#DC2626]/20 hover:-translate-y-1",
    uiverse: "btn-31",
  };

  return (
    <Tag
      href={href || undefined}
      className={cn(baseStyles, !isUiverse && "rounded-full", variantStyles[variant], className)}
      {...props}
    >
      {isUiverse ? (
        <span className="text-container">
          <span className="text flex items-center gap-2">{children}</span>
        </span>
      ) : (
        children
      )}
    </Tag>
  );
};
