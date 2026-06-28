import React from "react";
import { motion } from "framer-motion";

const seededValue = (index, seed = 42) => {
  const value = Math.sin(index * 43.11 + seed) * 10000;
  return value - Math.floor(value);
};

export default function PersonalityHUD({ status = "idle", mode = "default" }) {
  // 🧠 NEURAL_NODE_GENERATOR: Visualizing Behavioral Logic
  const nodes = Array.from({ length: 12 }).map((_, i) => ({
    id: i,
    x: seededValue(i, 1) * 100,
    y: seededValue(i, 2) * 100,
    size: 2 + seededValue(i, 3) * 6
  }));

  const activeColor = status === "thinking" ? "rgba(0, 240, 255, 0.8)" : 
                    status === "listening" ? "rgba(255, 185, 0, 0.8)" : 
                    "rgba(0, 240, 255, 0.4)";

  return (
    <motion.div 
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      className="fixed top-32 right-10 w-80 stark-panel p-6 flex flex-col gap-4 z-[100]"
    >
      <div className="flex justify-between items-center">
        <div className="flex flex-col">
          <span className="text-[10px] font-black tracking-[0.3em] uppercase text-white/40">Neural_Link</span>
          <span className="text-[14px] font-black tracking-[0.2em] uppercase italic text-cyan-400">BEHAVIORAL_CORE</span>
        </div>
        <div className="flex gap-1">
            {[1, 2, 3].map(i => (
                <motion.div 
                    key={i}
                    animate={{ opacity: [0.2, 1, 0.2] }}
                    transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                    className="w-1 h-3 bg-cyan-500/40"
                />
            ))}
        </div>
      </div>

      {/* 🧬 BEHAVIORAL_MAP (Neural Node Grid) */}
      <div className="relative w-full h-32 bg-black/40 border border-white/5 overflow-hidden rounded-xs">
          <div className="absolute inset-0 scanline" />
          <svg className="w-full h-full">
              {nodes.map((node) => (
                  <motion.circle 
                    key={node.id}
                    cx={`${node.x}%`}
                    cy={`${node.y}%`}
                    r={node.size / 2}
                    fill={activeColor}
                    animate={{ 
                        opacity: [0.1, 0.8, 0.1],
                        scale: [1, 1.2, 1]
                    }}
                    transition={{ 
                        duration: 2 + seededValue(node.id, 5) * 3, 
                        repeat: Infinity,
                        delay: seededValue(node.id, 6) * 2
                    }}
                  />
              ))}
              {/* Connection Lines (Simulated) */}
              <motion.path 
                d="M 10,10 L 90,90 M 90,10 L 10,90"
                stroke={activeColor}
                strokeWidth="0.5"
                strokeDasharray="4 8"
                opacity="0.1"
              />
          </svg>
          <div className="absolute bottom-2 left-2 flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
              <span className="text-[7px] font-mono tracking-widest text-white/40">NODE_SYNC: STABLE</span>
          </div>
      </div>

      <div className="flex flex-col gap-3 mt-2">
          <div className="flex justify-between items-end border-b border-white/5 pb-2">
              <span className="text-[9px] font-mono uppercase tracking-tighter opacity-60">Status_Resonance</span>
              <span className="text-[12px] font-black text-white">{status.toUpperCase()}</span>
          </div>
          <div className="flex justify-between items-end border-b border-white/5 pb-2">
              <span className="text-[9px] font-mono uppercase tracking-tighter opacity-60">Logical_Hardening</span>
              <span className="text-[12px] font-black text-white">99.9%</span>
          </div>
          <div className="flex justify-between items-end">
              <span className="text-[9px] font-mono uppercase tracking-tighter opacity-60">Sovereign_Protocol</span>
              <span className="text-[12px] font-black text-cyan-400">ACTIVE</span>
          </div>
      </div>
      
      {/* 🧪 O.M.E.G.A. PARITY: HIERARCHICAL_BORDERS */}
      <div className="absolute -right-[1px] top-4 bottom-4 w-[2px] bg-cyan-500/30" />
    </motion.div>
  );
}
