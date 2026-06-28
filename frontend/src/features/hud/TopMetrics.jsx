import React from "react";
import { motion } from "framer-motion";

export default function TopMetrics({ onDiagnostic, status }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="top-metrics pointer-events-auto cursor-pointer w-full flex flex-col items-end gap-1"
      onClick={onDiagnostic}
    >
      <div className="flex justify-between items-center w-full font-mono text-[8px] tracking-[0.2em] uppercase bg-black/40 px-3 py-1 rounded-sm border border-cyan-500/20 shadow-[0_0_15px_rgba(0,0,0,0.5)]">
         <span className="text-cyan-500/60 font-bold">OS_VERSION</span>
         <span className="text-cyan-400 font-black animate-pulse">O.M.E.G.A. XXX</span>
      </div>
      
      <div className="flex justify-between w-full font-mono text-[7px] tracking-[0.3em] uppercase opacity-60">
        <div className="flex gap-1">
          <span className="text-white/40">PACKET_STABILITY:</span>
          <span className="text-green-400 font-bold">NOMINAL</span>
        </div>
        <div className="flex gap-1">
          <span className="text-white/40">AURA_COEF:</span>
          <span className="text-cyan-400 font-bold">{status === "thinking" ? "SYNC..." : "9.97"}</span>
        </div>
      </div>
    </motion.div>
  );
}
