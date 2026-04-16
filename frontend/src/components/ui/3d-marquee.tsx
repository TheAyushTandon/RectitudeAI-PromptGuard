"use client";

import { motion } from "motion/react";
import { cn } from "../../lib/utils";

const LogoCard = () => (
    <div className="flex items-center gap-6 px-12 py-8 rounded-2xl bg-[#2e2e2e] border border-[#DC2626]/40 shadow-[0_0_30px_rgba(0,0,0,0.5)] min-w-[450px] group transition-all duration-300 hover:border-[#DC2626]/80 hover:bg-[#363636] hover:shadow-[0_0_40px_rgba(220,38,38,0.2)]">
      <img src="/logo.svg" alt="logo" className="w-16 h-16 brightness-0 invert opacity-90 group-hover:opacity-100 transition-opacity" />
      <span className="text-5xl font-black text-[#FFFFFF] tracking-widest font-sans uppercase">Rectitude<span className="text-[#DC2626]">.AI</span></span>
    </div>
);

export const ThreeDMarquee = ({
  className,
  count = 32, // Increased density for the "wall" effect
}: {
  className?: string;
  count?: number;
}) => {
  // We'll create 4 chunks of LogoCards
  const chunks = Array.from({ length: 4 }, () => 
    Array.from({ length: Math.ceil(count / 4) }, (_, i) => i)
  );

  return (
    <div
      className={cn(
        "mx-auto block h-[600px] overflow-hidden rounded-3xl max-sm:h-100 bg-neutral-900/10",
        className,
      )}
    >
      <div className="flex size-full items-center justify-center">
        {/* Adjusted scale and position to ensure depth and visibility */}
        <div className="size-[1720px] shrink-0 scale-[0.6] sm:scale-[0.85] lg:scale-100 transition-transform duration-500">
          <div
            style={{
              transform: "rotateX(55deg) rotateY(0deg) rotateZ(-45deg)",
            }}
            // Adjusted alignment to center the wall vertically
            className="relative top-[450px] left-1/4 grid size-full origin-top-left grid-cols-4 gap-12 transform-3d"
          >
            {chunks.map((subarray, colIndex) => (
              <motion.div
                animate={{ y: colIndex % 2 === 0 ? 250 : -250 }}
                transition={{
                  duration: colIndex % 2 === 0 ? 15 : 22,
                  repeat: Infinity,
                  repeatType: "reverse",
                  ease: "easeInOut",
                }}
                key={colIndex + "marquee"}
                className="flex flex-col items-start gap-12"
              >
                <GridLineVertical className="-left-6" offset="100px" />
                {subarray.map((_, itemIndex) => (
                  <div className="relative" key={itemIndex + "logo"}>
                    <GridLineHorizontal className="-top-6" offset="30px" />
                    <motion.div
                      whileHover={{
                        y: -20,
                        scale: 1.05,
                        zIndex: 50,
                      }}
                      transition={{
                        duration: 0.4,
                        ease: "easeOut",
                      }}
                    >
                      <LogoCard />
                    </motion.div>
                  </div>
                ))}
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const GridLineHorizontal = ({
  className,
  offset,
}: {
  className?: string;
  offset?: string;
}) => {
  return (
    <div
      style={
        {
          "--background": "#ffffff",
          "--color": "rgba(255, 255, 255, 0.15)",
          "--height": "1px",
          "--width": "5px",
          "--fade-stop": "90%",
          "--offset": offset || "200px",
          "--color-dark": "rgba(255, 255, 255, 0.15)",
          maskComposite: "exclude",
        } as React.CSSProperties
      }
      className={cn(
        "absolute left-[calc(var(--offset)/2*-1)] h-[var(--height)] w-[calc(100%+var(--offset))]",
        "bg-[linear-gradient(to_right,var(--color),var(--color)_50%,transparent_0,transparent)]",
        "[background-size:var(--width)_var(--height)]",
        "[mask:linear-gradient(to_left,var(--background)_var(--fade-stop),transparent),_linear-gradient(to_right,var(--background)_var(--fade-stop),transparent),_linear-gradient(black,black)]",
        "[mask-composite:exclude]",
        "z-30",
        "dark:bg-[linear-gradient(to_right,var(--color-dark),var(--color-dark)_50%,transparent_0,transparent)]",
        className,
      )}
    ></div>
  );
};

const GridLineVertical = ({
  className,
  offset,
}: {
  className?: string;
  offset?: string;
}) => {
  return (
    <div
      style={
        {
          "--background": "#ffffff",
          "--color": "rgba(255, 255, 255, 0.15)",
          "--height": "5px",
          "--width": "1px",
          "--fade-stop": "90%",
          "--offset": offset || "150px",
          "--color-dark": "rgba(255, 255, 255, 0.15)",
          maskComposite: "exclude",
        } as React.CSSProperties
      }
      className={cn(
        "absolute top-[calc(var(--offset)/2*-1)] h-[calc(100%+var(--offset))] w-[var(--width)]",
        "bg-[linear-gradient(to_bottom,var(--color),var(--color)_50%,transparent_0,transparent)]",
        "[background-size:var(--width)_var(--height)]",
        "[mask:linear-gradient(to_top,var(--background)_var(--fade-stop),transparent),_linear-gradient(to_bottom,var(--background)_var(--fade-stop),transparent),_linear-gradient(black,black)]",
        "[mask-composite:exclude]",
        "z-30",
        "dark:bg-[linear-gradient(to_bottom,var(--color-dark),var(--color-dark)_50%,transparent_0,transparent)]",
        className,
      )}
    ></div>
  );
};
