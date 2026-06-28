import React, { useMemo } from "react";
import { motion } from "framer-motion";

const getSimulationId = (data) => {
  const source = JSON.stringify(data);
  let hash = 0;

  for (let i = 0; i < source.length; i++) {
    hash = (hash * 31 + source.charCodeAt(i)) >>> 0;
  }

  return hash.toString(16).slice(0, 6).padStart(6, "0").toUpperCase();
};

export default function SuitSimulationHUD({ data }) {
  const simulationId = useMemo(() => getSimulationId(data), [data]);
  if (!data) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, x: 100 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 100 }}
      className="fixed right-12 top-40 z-[110] w-[320px] bg-black/60 backdrop-blur-xl border-r-2 border-cyan-500/30 p-6 rounded-l-3xl shadow-[0_0_50px_rgba(0,240,255,0.1)]"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <span className="font-mono text-[10px] tracking-[0.3em] uppercase text-cyan-400">Nano_Construct_V4</span>
        </div>
        <span className="text-[9px] text-cyan-500/40 font-mono">SIM_ID: {simulationId}</span>
      </div>

      {/* 🚀 Nano-Suit Schematic (Simplified Vector) */}
      <div className="relative w-full h-64 flex items-center justify-center mb-6 overflow-hidden">
        <svg viewBox="0 0 100 100" className="w-full h-full text-cyan-500/20">
          {/* Iron Man Helmet Silhouette */}
          <motion.path 
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2, repeat: Infinity }}
            d="M50 10 C30 10 20 30 20 50 C20 70 30 90 50 90 C70 90 80 70 80 50 C80 30 70 10 50 10 Z" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="0.5" 
          />
          {/* Internal Circuits */}
          <motion.circle cx="50" cy="40" r="15" stroke="currentColor" strokeWidth="0.2" fill="none" animate={{ opacity: [0.1, 0.5, 0.1] }} transition={{ duration: 3, repeat: Infinity }} />
          <motion.line x1="20" y1="50" x2="80" y2="50" stroke="currentColor" strokeWidth="0.2" strokeDasharray="2 2" />
          <motion.line x1="50" y1="10" x2="50" y2="90" stroke="currentColor" strokeWidth="0.2" strokeDasharray="2 2" />
        </svg>

        {/* 💠 Particle Pulse (Nanotech effect) */}
        <div className="absolute inset-0 flex items-center justify-center">
            {Array.from({ length: 8 }).map((_, i) => (
                <motion.div 
                    key={i}
                    animate={{ 
                        scale: [1, 2], 
                        opacity: [0.4, 0],
                        rotate: i * 45
                    }}
                    transition={{ duration: 2, repeat: Infinity, delay: i * 0.2 }}
                    className="absolute w-20 h-[1px] bg-cyan-400/40"
                />
            ))}
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex justify-between items-end">
            <span className="text-[9px] text-cyan-500/60 font-mono">PARTICLE_DENSITY</span>
            <span className="text-xs font-mono text-cyan-400">{data.particles || "99.82%"}</span>
        </div>
        <div className="w-full h-1 bg-cyan-900/40 rounded-full overflow-hidden">
            <motion.div 
               initial={{ width: 0 }}
               animate={{ width: data.particles }} 
               className="h-full bg-cyan-400 shadow-[0_0_10px_cyan]"
            />
        </div>

        <div className="grid grid-cols-2 gap-4 mt-6">
            <div className="flex flex-col gap-1">
                <span className="text-[8px] text-cyan-500/40 uppercase">Molecular_Sync</span>
                <span className="text-[10px] text-cyan-400 font-mono">{data.molecular_sync}</span>
            </div>
            <div className="flex flex-col gap-1 text-right">
                <span className="text-[8px] text-cyan-500/40 uppercase">Reactor_State</span>
                <span className="text-[10px] text-green-400 font-mono">{data.reactor}</span>
            </div>
        </div>
      </div>

      {/* Footer Diagnostic Status */}
      <div className="mt-8 pt-4 border-t border-cyan-500/10 flex items-center gap-4 text-[9px] font-mono text-cyan-500/30">
          <span className="flex items-center gap-1"><div className="w-1 h-1 rounded-full bg-green-500" /> STABLE</span>
          <span>AUTOREPAIR: ACTIVE</span>
      </div>
    </motion.div>
  );
}
