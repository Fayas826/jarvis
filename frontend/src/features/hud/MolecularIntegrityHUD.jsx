import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function MolecularIntegrityHUD({ active }) {
  const [sectors, setSectors] = useState([
    { name: "CHEST_PLATE", health: 100, status: "SYNCED" },
    { name: "RIGHT_GAUNTLET", health: 100, status: "READY" },
    { name: "LEFT_GAUNTLET", health: 100, status: "READY" },
    { name: "HELMET_SEAL", health: 100, status: "LOCKED" },
    { name: "FLIGHT_STABILIZERS", health: 100, status: "ACTIVE" }
  ]);

  useEffect(() => {
    if (!active) return;
    const interval = setInterval(() => {
      // Small jitter for cinematic effect
      setSectors(prev => prev.map(s => ({
        ...s,
        health: Math.min(100, 99.8 + Math.random() * 0.2) 
      })));
    }, 3000);
    return () => clearInterval(interval);
  }, [active]);

  if (!active) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, x: -100 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -100 }}
      className="fixed left-64 top-40 z-[115] w-[200px] zenith-glass p-4 rounded-xl border border-cyan-500/20 shadow-[0_0_50px_rgba(0,0,0,0.6)]"
    >
      <div className="flex flex-col gap-1 mb-4">
         <div className="flex justify-between items-center px-1">
            <span className="text-[7px] text-cyan-400 font-black tracking-[0.3em] uppercase">NEURAL_INTEGRITY</span>
            <div className="w-1 h-3 bg-cyan-400 shadow-[0_0_10px_cyan]" />
         </div>
         <div className="w-full h-[1px] bg-gradient-to-r from-cyan-500/30 to-transparent" />
      </div>

      <div className="space-y-4">
         {sectors.map((sector, i) => (
             <div key={i} className="flex flex-col gap-1.5">
                <div className="flex justify-between items-end px-1">
                    <span className="text-[7px] text-cyan-600/60 font-black uppercase tracking-widest leading-none">{sector.name}</span>
                    <span className="text-[8px] text-cyan-400 font-mono leading-none">{sector.health.toFixed(1)}%</span>
                </div>
                <div className="w-full h-[1.5px] bg-white/5 rounded-full overflow-hidden relative">
                    <motion.div 
                       initial={{ width: 0 }}
                       animate={{ width: `${sector.health}%` }}
                       className="h-full bg-gradient-to-r from-cyan-600 to-cyan-300 shadow-[0_0_8px_cyan]"
                    />
                </div>
             </div>
         ))}
      </div>

      {/* 🧬 Prism-Shift side-accent */}
      <div className="absolute -left-[2px] top-1/2 -translate-y-1/2 h-2/3 w-[2px] bg-gradient-to-b from-transparent via-cyan-400 to-transparent opacity-60" />

      {/* Footer System Status */}
      <div className="mt-4 pt-2 border-t border-cyan-500/10 text-right">
          <span className="text-[6px] font-mono text-cyan-400/40 tracking-[0.2em] uppercase">
             SYNC: 100%
          </span>
      </div>
    </motion.div>
  );
}
