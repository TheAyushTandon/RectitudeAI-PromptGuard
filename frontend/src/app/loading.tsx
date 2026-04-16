export default function Loading() {
  return (
    <div className="fixed inset-0 z-[9999] bg-[#1A1A1A] flex flex-col items-center justify-center">
      <div className="relative flex items-center justify-center">
        {/* Outer glowing ring */}
        <div className="absolute w-24 h-24 border-t-2 border-[#DC2626] rounded-full animate-spin [animation-duration:1.5s]" />
        
        {/* Inner reverse spinning ring */}
        <div className="absolute w-16 h-16 border-b-2 border-[#EAB308] rounded-full animate-spin [animation-direction:reverse] [animation-duration:1s]" />
        
        {/* Center steady pulse */}
        <div className="w-8 h-8 bg-[#DC2626] rounded-full animate-pulse shadow-[0_0_20px_rgba(220,38,38,0.8)]" />
      </div>
      
      <div className="mt-8 font-mono text-sm tracking-[0.3em] text-[#A1A1AA] uppercase animate-pulse">
        Initializing Base...
      </div>
    </div>
  );
}
