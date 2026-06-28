import React from "react";
import { motion } from "framer-motion";

export default function PropulsionControl({ mousePos, active }) {
  if (!active) return null;

  // Simulate flight tilts based on mouse position
  const tiltX = (mousePos.y / window.innerHeight - 0.5) * 30; // Pitch
  const tiltY = (mousePos.x / window.innerWidth - 0.5) * -30; // Roll
  const velocity = Math.round(4200 + Math.hypot(tiltX, tiltY) * 1.2);

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      style={{ 
        perspective: "1000px", 
        rotateX: `${tiltX}deg`, 
        rotateY: `${tiltY}deg` 
      }}
      className="fixed bottom-40 left-10 z-[120] w-48 h-48 pointer-events-none"
    >
      {/* 🚀 Flight Dynamics Ring */}
      <div className="absolute inset-0 rounded-full border border-cyan-500/20 zenith-glass shadow-[0_0_40px_rgba(0,240,255,0.1)] flex items-center justify-center">
         <motion.div 
           animate={{ rotate: 360 }}
           transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
           className="absolute inset-2 rounded-full border border-dashed border-cyan-400/5"
         />
         
         <div className="w-full h-[0.5px] bg-cyan-400/20 relative" />

         {/* 💠 Core Stability Indicator */}
         <div className="w-12 h-12 rounded-full border border-cyan-400/20 flex items-center justify-center relative">
            <motion.div 
               animate={{ 
                   scale: [1, 1.2, 1],
                   opacity: [0.3, 0.6, 0.3]
               }}
               transition={{ duration: 2, repeat: Infinity }}
               className="w-4 h-4 rounded-full bg-cyan-400/60 shadow-[0_0_15px_cyan]"
            />
         </div>
      </div>

      {/* ⚡ Thrust Bars (Compact) */}
      <div className="absolute -left-4 top-1/2 -translate-y-1/2 h-24 w-1.5 flex flex-col gap-2">
         <div className="flex-1 bg-cyan-900/20 rounded-full overflow-hidden border border-cyan-500/10">
            <motion.div 
               animate={{ height: ["70%", "90%", "70%"] }}
               transition={{ duration: 1, repeat: Infinity }}
               className="absolute bottom-0 w-full bg-cyan-400/60 shadow-[0_0_10px_cyan]"
            />
         </div>
      </div>

      <div className="absolute -right-4 top-1/2 -translate-y-1/2 h-24 w-1.5 flex flex-col gap-2">
         <div className="flex-1 bg-cyan-900/20 rounded-full overflow-hidden border border-cyan-500/10">
            <motion.div 
               animate={{ height: ["65%", "85%", "65%"] }}
               transition={{ duration: 1.2, repeat: Infinity }}
               className="absolute bottom-0 w-full bg-cyan-400/60 shadow-[0_0_10px_cyan]"
            />
         </div>
      </div>

      {/* 🚀 Velocity Display */}
      <div className="absolute -top-12 left-1/2 -translate-x-1/2 flex flex-col items-center">
          <span className="text-[6px] font-mono text-cyan-500/30 tracking-[0.4em] uppercase">V_IND_SYNC</span>
          <div className="text-xl font-black font-mono text-cyan-400">
             {velocity} <span className="text-[8px] opacity-40">KM/H</span>
          </div>
      </div>
    </motion.div>
  );
}
