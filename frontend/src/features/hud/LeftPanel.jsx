import React from "react";
import { motion } from "framer-motion";

export default function LeftPanel() {
  return (
    <motion.div 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="panel-left zenith-glass p-4 w-[220px] flex flex-col gap-6 overflow-hidden border-r border-cyan-500/10 shadow-[20px_0_50px_rgba(0,0,0,0.4)]"
    >
      {/* 📡 ZENITH_SIGNAL_HEADER */}
      <div className="flex flex-col gap-1 holo-effect">
         <div className="flex justify-between items-center px-1">
            <span className="text-[8px] text-cyan-400 font-black tracking-[0.3em] uppercase">NEURAL_DEEP_LINK</span>
            <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_10px_cyan]" />
         </div>
         <div className="w-full h-px bg-linear-to-r from-cyan-500/30 to-transparent" />
      </div>

      {/* 🛰️ TACTICAL_RADAR_V4 */}
      <div className="relative flex flex-col items-center justify-center py-4">
        <div className="relative border border-cyan-500/20 rounded-full w-24 h-24 flex items-center justify-center">
            {/* Pulsing Grid Rings */}
            <motion.div 
                animate={{ scale: [1, 1.2, 1], opacity: [0.1, 0.3, 0.1] }}
                transition={{ duration: 4, repeat: Infinity }}
                className="absolute inset-0 border border-cyan-400/20 rounded-full"
            />
            <motion.div 
                animate={{ rotate: 360 }}
                transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                className="absolute inset-0 border-t border-cyan-400/40 rounded-full"
            />
            
            {/* Scanning Sweep */}
            <motion.div 
                animate={{ rotate: 360 }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                className="absolute inset-0 bg-linear-to-r from-cyan-500/10 to-transparent rounded-full origin-center"
                style={{ clipPath: "polygon(50% 50%, 100% 0, 100% 100%)" }}
            />

            <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full shadow-[0_0_12px_cyan]" />
        </div>
      </div>

      <div className="flex flex-col gap-3 font-mono text-[9px] tracking-widest uppercase mt-2">
        <div className="flex justify-between border-b border-white/5 pb-1.5">
            <span className="opacity-40">Lat_Coord</span>
            <span className="text-cyan-400">28.61° N</span>
        </div>
        <div className="flex justify-between border-b border-white/5 pb-1.5">
            <span className="opacity-40">Lon_Coord</span>
            <span className="text-cyan-400">77.20° E</span>
        </div>
        <div className="flex justify-between items-center text-cyan-400/80 font-black">
            <span>Signal_Lock</span>
            <motion.span 
                animate={{ opacity: [0.4, 1, 0.4] }}
                transition={{ duration: 1.5, repeat: Infinity }}
            >
                STABLE
            </motion.span>
        </div>
      </div>

      <div className="mt-auto pt-4 border-t border-cyan-500/10 flex flex-col gap-1">
         <span className="text-[6px] text-cyan-500/30 uppercase tracking-[0.4em]">Auth: Active</span>
         <span className="text-[8px] text-cyan-400 font-black">STARK_GLOBAL_NAV</span>
      </div>
    </motion.div>
  );
}
