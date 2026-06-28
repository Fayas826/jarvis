import React, { useState, useEffect, useMemo } from "react";
import { motion } from "framer-motion";

const seededValue = (index, seed = 17) => {
  const value = Math.sin(index * 91.7 + seed) * 10000;
  return value - Math.floor(value);
};

export default function VitalsMonitor({ status }) {
  const [metrics, setMetrics] = useState({
    cpu: 18,
    ram: 42.4,
    neural: 98,
    sync: 100
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics({
        cpu: Math.floor(Math.random() * 10) + 15,
        ram: 42.4 + (Math.random() * 0.1),
        neural: 97 + Math.floor(Math.random() * 3),
        sync: 99.8 + (Math.random() * 0.2)
      });
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const isActive = status === 'thinking' || status === 'speaking';
  const fluxHeights = useMemo(() => {
    return Array.from({ length: 32 }, (_, i) => ({
      active: 20 + seededValue(i, 41) * 15,
      idle: 10 + seededValue(i, 73) * 8
    }));
  }, []);

  return (
    <motion.div 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex flex-col gap-3 p-3 w-full relative overflow-hidden rounded-[2px] border border-cyan-500/30 bg-linear-to-br from-[#000a12]/90 to-[#001726]/90 backdrop-blur-xl shadow-[0_0_20px_rgba(0,0,0,0.8)]"
    >
      {/* 🧬 ZENITH_BIOMETRIC_HEADER */}
      <div className="flex flex-col gap-1.5 relative">
         <div className="flex justify-between items-center px-1">
            <span className="text-[9px] text-cyan-400 font-black tracking-[0.2em] uppercase drop-shadow-[0_0_8px_cyan]">BIOMETRIC_STABILITY_V4</span>
            <div className={`w-2 h-2 rounded-full ${isActive ? 'bg-amber-400 animate-pulse shadow-[0_0_10px_#fbbf24]' : 'bg-cyan-400 shadow-[0_0_10px_cyan]'}`} />
         </div>
         <div className="w-[60%] h-px bg-cyan-500/40" />
      </div>

      {/* 📊 ZENITH_METRICS_GRID (HIGH-DENSITY) */}
      <div className="grid grid-cols-2 gap-y-4 gap-x-2 px-1">
        <div className="flex flex-col gap-1">
            <span className="text-[7px] text-cyan-500/60 uppercase tracking-widest font-black">Neural_Sync</span>
            <span className="text-[12px] font-black text-cyan-400 font-mono tracking-wide drop-shadow-[0_0_5px_cyan]">{metrics.sync.toFixed(1)}%</span>
        </div>
        <div className="flex flex-col gap-1 pl-2">
            <span className="text-[7px] text-cyan-500/60 uppercase tracking-widest font-black">Core_Load</span>
            <span className="text-[12px] font-black text-cyan-400 font-mono tracking-wide drop-shadow-[0_0_5px_cyan]">{metrics.cpu}%</span>
        </div>
        <div className="flex flex-col gap-1">
            <span className="text-[7px] text-cyan-500/60 uppercase tracking-widest font-black">Memory_Cap</span>
            <span className="text-[12px] font-black text-cyan-400 font-mono tracking-wide drop-shadow-[0_0_5px_cyan]">{metrics.ram.toFixed(1)}GB</span>
        </div>
        <div className="flex flex-col gap-1 pl-2">
            <span className="text-[7px] text-cyan-500/60 uppercase tracking-widest font-black">Neural_Hunt</span>
            <span className="text-[12px] font-black text-cyan-400 font-mono tracking-wide drop-shadow-[0_0_5px_cyan]">{metrics.neural}%</span>
        </div>
      </div>

      {/* 💓 ZENITH_QUANTUM_HEARTBEAT (PRISM_SHIFT) */}
      <div className="flex flex-col gap-3 mt-2">
          <span className="text-[7px] text-cyan-500/40 uppercase tracking-[0.3em]">Synaptic_Flux_Pattern</span>
          <div className="h-12 w-full flex items-end justify-center gap-[2px] overflow-visible">
             {Array.from({ length: 32 }).map((_, i) => (
                 <motion.div
                    key={i}
                    animate={{ 
                        height: isActive ? [4, fluxHeights[i].active, 4] : [4, fluxHeights[i].idle, 4],
                        backgroundColor: isActive ? 'rgba(251, 191, 36, 0.8)' : 'rgba(34, 211, 238, 0.4)',
                        opacity: [0.3, 1, 0.3]
                    }}
                    transition={{ 
                        duration: 0.2, 
                        repeat: Infinity, 
                        delay: i * 0.03,
                        ease: "linear"
                    }}
                    className="w-[2px] rounded-t-full shadow-[0_0_5px_currentColor]"
                 />
             ))}
          </div>
      </div>

      <div className="mt-1 flex items-center gap-2 pt-1 px-1">
         <span className="text-[7px] font-mono tracking-widest text-cyan-500/30 uppercase font-black">SYNAPTIC_FLUX_PATTERN</span>
      </div>
    </motion.div>
  );
}
